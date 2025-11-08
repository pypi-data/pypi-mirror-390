# -*- coding: utf-8 -*-
#
# Copyright (C) 2020, 2021, 2023 ONERA <Judicael.Bedouet@onera.fr>
#
# This file is part of PyATMLab'.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
runner.py: Main module to run SINAPS with different scenarios

History
=======
1.0.0 (2020, August 4th)
Initial version

1.1.0 (2020, October 9th)
Add black/white lists
Set CO constants

1.2.0 (2020, October 19th)
CO constants become parameters of the CO init

1.3.0 (2020, October 22th)
Split the main program into different mains.
Add yaml files to configure the different mains.

1.4.0 (2020, October 26th)
Create the class Configuration

1.5.0 (2020, November 5th)
Add smoothing

1.6.0 (2021, February 18th)
SINAPIS/SINAPS 1.4/1.4
One scenario ID per day

"""

from collections import defaultdict
import datetime
import json
import os
import pprint

import traceback
from typing import TextIO

from atmlab.common.wsclient.configuration import Configuration
from atmlab.common.wsclient.server_url_connection import ServerURLConnection
from atmlab.sinaps.sector_configuration_solution import Collapsing, ShouldCollapse
from atmlab.sinaps.sector_filter import BlackListElement, WhiteListElement
from atmlab.sinapsis.html_counts_generator import HtmlCountsGenerator
from atmlab.sinapsis.otmv import OTMV
from atmlab.sinapsis.traffic_counts import TrafficCounts, TrafficType
from atmlab.sinapsis.traffic_counts_plot import TrafficCountsPlot
from atmlab.sinapsis.uces import Uces, from_sector_configuration_plan
from atmlab.sinapsis.uceso import UC, Uceso, write_ucesos
from atmlab.sinapsis.wsclient.scenario_factory import ScenarioFactory

from .cows import COWS


class Runner(object):

    DAY_FORMAT = "%Y-%m-%d"

    def __init__(self, specific_yaml_filename, argv) -> None:
        self.conf = Configuration(specific_yaml_filename, argv)
        self.conn = ServerURLConnection(
            self.conf.auth_url,
            self.conf.username,
            self.conf.password,
            self.conf.proxies,
            self.conf.timeout,
            verbose=self.conf.verbose
        )
        self.factory = ScenarioFactory(self.conn, self.conf.sinapsis_url, self.conf.nest_compression)
        if 'password' in self.conf.data:
            del self.conf.data['password']
        self.data = self.conf.data
        if self.conf.verbose:
            print()
            print('Final configuration is:')
            pprint.pprint(self.conf.data)
            print()
    
    def run(self, results_dir, scn_id, keep_days=None) -> None:

        # TODO append_conf is now deprecated.

        plan_filename = self.data['plan_filename'] if 'plan_filename' in self.data else results_dir + '.txt'
        # Clear the contents of the file
        with open(plan_filename, 'w'):
            pass

        sub_scenarios = self.factory.get_scenarios(scn_id)
        print("Found the following sub scenarios")
        for sub_scenario, sub_scn_id in sub_scenarios.items():
            print(sub_scenario, ":", sub_scn_id)

        black_list = []
        if self.conf.black_list:
            black_list = [BlackListElement(tvId, None, None) for tvId in self.conf.black_list]

        white_list = []
        if self.conf.white_list:
            white_list = [WhiteListElement(tvId, False, None, None) for tvId in self.conf.white_list]

        all_status = []

        for scn_date, sub_scn_id in sub_scenarios.items():
            if keep_days and scn_date not in keep_days:
                continue
            self.run_one_day(scn_date, sub_scn_id, black_list, white_list, all_status, plan_filename, results_dir)

        self.factory.release_scenario(scn_id)

        ok = True
        print()
        for status in all_status:
            if status['value'] != 'OK':
                print("==========", "[" + status['value'] + "]", status['currentTime'][0:10], "==========")
                print("\t", status["reason"])
                ok = False
        if ok:
            print("OK")
        print()
    
    def run_one_day(self, scn_date, scn_id, black_list, white_list, all_status, plan_filename, results_dir) -> None:
        one_day_runner = OneDayRunner(self, scn_date, scn_id, black_list, white_list, all_status, plan_filename, results_dir)
        return one_day_runner.run()


class OneDayRunner(object):

    def __init__(self, runner: Runner, scn_date, scn_id, black_list, white_list, all_status: list, plan_filename, results_dir) -> None:
        self._runner = runner
        self._scn_date = scn_date
        self._scn_id = scn_id
        self._black_list = black_list
        self._white_list = white_list
        self._all_status = all_status
        self._plan_filename = plan_filename
        self._results_dir = results_dir
        self.html_generator : HtmlCountsGenerator | None = None
        
    def run(self) -> None:
        try:
            self._prepare()
            if self._runner.conf.optimise_uceso:
                self._optimise_uceso()
            self._run()
        finally:
            if self._co:
                del self._co
            self._runner.factory.release_scenario(self._scn_id)

    def _prepare(self) -> None:

        print()
        print("RUN SINAPS PREDICT for", self._scn_date, '<', self._scn_id, '>')
        print()

        if self._runner.conf.overloading_catalog:
            self._runner.factory.init_scenario(self._scn_id, str(self._runner.conf.overloading_catalog))
        self._scenario = self._runner.factory.get_scenario(self._scn_id)

        status = self._scenario.get_status()
        self._all_status.append(status)

        period = self._scenario.get_period()
        self._wef = datetime.datetime.strptime(period['wef'], '%Y-%m-%d %H:%M')
        self._unt = datetime.datetime.strptime(period['unt'], '%Y-%m-%d %H:%M')
        print('Period is [%s, %s]' % (period['wef'], period['unt']))
        print('Current time is %s' % (self._scenario.get_current_time(),))
        print('Catalog is %s' % (self._scenario.get_catalog_name(),))

        if self._runner.conf.apex:
            print("Set APEX definitions:")
            for apex in self._runner.conf.apex:
                print("\t", apex)
            self._scenario.set_apex_definitions(self._runner.conf.apex)

        print('Initializing SINAPS optimizer...')
        self._co = COWS(self._runner.conn, self._runner.conf.sinaps_url, self._scn_id,
                    average_over_peak=self._runner.conf.average_over_peak,
                    instantaneous_over_peak=self._runner.conf.instantaneous_over_peak,
                    minimum_distinct_peak=self._runner.conf.minimum_distinct_peak,
                    minimum_overload_time=self._runner.conf.minimum_overload_time,
                    minimum_sector_time=self._runner.conf.minimum_sector_time,
                    rating_threshold=self._runner.conf.rating_threshold,
                    rounded_to=self._runner.conf.rounded_to,
                    smooth_act_half_window=self._runner.conf.smooth_act_half_window,
                    smooth_ifpl_half_window=self._runner.conf.smooth_ifpl_half_window,
        )

        print("Whitelisting %i sectors" % (len(self._white_list),))
        self._co.set_white_list(self._white_list)

        print("Blacklisting %i sectors" % (len(self._black_list),))
        self._co.set_black_list(self._black_list)

    def _run(self) -> None:

        print('Getting the popular path...')
        path = self._co.popular_path()

        self.overloaded_periods = defaultdict(list)
        for period in self._co.overloaded_periods():
            self.overloaded_periods[period.tvId].append((period.wef, period.unt))
        
        wef = self._wef.replace(tzinfo=datetime.timezone.utc)
        self.uces = from_sector_configuration_plan(path, wef)

        print('Write', self._plan_filename)
        self.uces.write(self._plan_filename, 'a')
        
        sectors = set(self._runner.conf.output_includes)
        sectors.update(self.uces.get_sectors())
        self._write_csv_files_and_image_traffic_counts(sectors, False)
        self._write_csv_files_and_image_traffic_counts(sectors, True)
    
    def _write_csv_files_and_image_traffic_counts(self, sectors, smoothing) -> None:
        date = self._wef.strftime('%Y_%m_%d')
        tv_results_dir = os.path.join(self._results_dir, date)
        suffix = "_s_%d_%d" % (self._runner.conf.smooth_act_half_window, self._runner.conf.smooth_ifpl_half_window) if smoothing else ""
        if self._runner.conf.output_html:
            print("Generate Traffic Counts files in", tv_results_dir + suffix)
            if not os.path.exists(tv_results_dir + suffix):
                os.makedirs(tv_results_dir + suffix)
            self.html_generator = HtmlCountsGenerator(tv_results_dir + suffix)
        for tv_id in sectors:
            try:
                self.write_csv_and_image_traffic_counts(tv_results_dir, tv_id, smoothing, suffix)
            except Exception:
                print('Can not download data for', tv_id)
                traceback.print_exc()
        if self.html_generator:
            self.html_generator.generate()

    def write_csv_and_image_traffic_counts(self, tv_results_dir, tv_id, smoothing, suffix) -> None:
        if self._runner.conf.output_csv:
            if not os.path.exists(tv_results_dir):
                os.makedirs(tv_results_dir)
            self._write_csv(tv_results_dir, tv_id, smoothing, suffix)
        if self._runner.conf.output_png:
            if not os.path.exists(tv_results_dir):
                os.makedirs(tv_results_dir)
            self._write_image_traffic_counts(tv_results_dir, tv_id, smoothing, suffix)
        if self.html_generator:
            self._write_html_traffic_counts(tv_results_dir + suffix, tv_id, smoothing)
    
    def _write_csv(self, tv_results_dir, tv_id, smoothing, suffix) -> None:
        filename = os.path.join(tv_results_dir, "%s%s.csv" % (tv_id, suffix))
        # Download the CSV file
        if not os.path.exists(filename):
            print('Downloading ' + filename)
            # Get data
            if smoothing:
                data = self._scenario.get_occupancy(tv_id,
                                            smooth_act_half_window=self._runner.conf.smooth_act_half_window,
                                            smooth_ifpl_half_window=self._runner.conf.smooth_ifpl_half_window,
                                                    )
            else:
                data = self._scenario.get_occupancy(tv_id)
            # Write data as a CSV file
            with open(filename, 'w') as csv:
                csv.write('wef;unt;totalCounts\n')
                for item in data['counts']['item']:
                    assert (item['value']['item'][0]['key'] == 'LOAD')
                    iwef = item['key']['wef']
                    iunt = item['key']['unt']
                    total_counts = item['value']['item'][0]['value']['totalCounts']
                    csv.write("%s;%s;%s\n" % (iwef, iunt, total_counts))
    
    def _write_image_traffic_counts(self, tv_results_dir, tv_id, smoothing, suffix) -> None:
        # Download the image file
        filename = os.path.join(tv_results_dir, "%s%s.png" % (tv_id, suffix))
        if not os.path.exists(filename):
            print('Downloading ' + filename)
            with open(filename, 'wb') as img:
                if smoothing:
                    self._scenario.copy_occupancy_img_to(img, tv_id, width=4000, height=800,
                                                    smooth_act_half_window=self._runner.conf.smooth_act_half_window,
                                                    smooth_ifpl_half_window=self._runner.conf.smooth_ifpl_half_window
                                                    )
                else:
                    self._scenario.copy_occupancy_img_to(img, tv_id, width=4000, height=800)
    
    def _write_html_traffic_counts(self, tv_results_dir, tv_id, smoothing) -> None:
        filename = os.path.join(tv_results_dir, "%s.json" % (tv_id, ))
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                if smoothing:
                    occupancy = self._scenario.occupancy_counts(tv_id,
                                                smooth_act_half_window=self._runner.conf.smooth_act_half_window,
                                                smooth_ifpl_half_window=self._runner.conf.smooth_ifpl_half_window,
                                                include_otmv_values=True
                                                )
                else:
                    occupancy = self._scenario.occupancy_counts(tv_id, include_otmv_values=True)
                json.dump(occupancy, f)
        else:
            with open(filename, 'r') as f:
                occupancy = json.load(f)
        self._generate_html(occupancy)
    
    def _generate_html(self, occupancy) -> None:
        all_traffic_counts = TrafficCounts.convert2(occupancy)
        traffic_counts = all_traffic_counts[TrafficType.LOAD]
        highligh_periods = self.uces.get_highlight_periods_of(traffic_counts.tv)
        overloaded_periods = self.overloaded_periods[traffic_counts.tv]
        assert not self.html_generator is None
        self.html_generator.add(traffic_counts, highligh_periods, overloaded_periods)
    
    def _optimise_uceso(self) -> None:
        # Download UCESO
        uceso = self._scenario.get_uceso_plan()
        day = self._scn_date.strftime(Runner.DAY_FORMAT)
        uceso_filename = os.path.join("..", "uceso", self._scenario.get_tv_set_id(), day + '.json')
        print('Write', uceso_filename)
        write_ucesos(uceso, uceso_filename)
        # Optimise UCESO
        loop = True
        while loop:
            loop = self._optimise_uceso_one()
    
    def _optimise_uceso_one(self):
        print('Getting the center hotspots...')
        chs = self._co.center_hotspots(delta_uceso_ucesa=-1)
        for hotspot in chs.the_hotspots:
            print("Detect hotspot from", hotspot.begin, "until", hotspot.end, "[", hotspot.ucesa, "/", hotspot.uceso, "]")
            wef = hotspot.begin # - datetime.timedelta(minutes=10)
            unt = hotspot.end # + datetime.timedelta(minutes=10)
            proposal : ShouldCollapse = self._co.propose_collapse(wef, unt, hotspot.ucesa)
            if proposal:
                print("White list", proposal.new_tv, "(", proposal.tv1, "+", proposal.tv2, ") from", wef, "until", unt, "[overload=", proposal.overload, "]")
                self._white_list.append(WhiteListElement(proposal.new_tv, True, wef, unt))
                self._co.set_white_list(self._white_list)
                return True
        return False
