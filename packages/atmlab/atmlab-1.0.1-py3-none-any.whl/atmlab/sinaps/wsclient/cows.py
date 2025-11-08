# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 ONERA <Judicael.Bedouet@onera.fr>
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

import datetime
from atmlab.sinaps.overloaded_period import OverloadedPeriod
from atmlab.common.wsclient.abstract_ws import AbstractWS
from atmlab.sinaps.center_hotspots import CenterHotSpots
from atmlab.sinaps.sector_configuration_solution import ShouldCollapse, type_of_sector_transition, SectorConfigurationSolution
from atmlab.sinaps.sector_filter import BlackListElement, WhiteListElement

import json
import urllib


class COWS(AbstractWS):

    PERIOD_FORMAT = "%Y-%m-%d %H:%M"

    def __init__(self, conn, base_url, scn_id,
                 anticipation=None,
                 average_over_peak=None,
                 instantaneous_over_peak=None,
                 minimum_distinct_peak=None,
                 minimum_overload_time=None,
                 minimum_sector_time=None,
                 overload_extra=None,
                 rating_threshold=None,
                 rounded_to=None,
                 smooth_act_half_window=None,
                 smooth_ifpl_half_window=None,
                 ):
        """Initialize an optimizer
        :param conn: Token to connect to the server
        :param base_url: SINAPS base URL
        :param scn_id: Scenario Identifier
        :param anticipation: Number of minutes to be added before and after once found an overload
        :param average_over_peak: Average occupancy over peak to consider an overload
        :param instantaneous_over_peak: Instantaneous occupancy value over peak to consider an overload
        :param minimum_distinct_peak: When two overloads are separated by less than Y4 minutes, consider them as a unique overload
        :param minimum_overload_time: Minimal number of minutes where occupancy is over peak to consider an overload
        :param minimum_sector_time: Minimum duration to keep a sector
        :param overload_extra: Add extra minutes before and after optimisation
        :param rating_threshold: Threshold value between 0 (keep all transitions) to 100 (keep only popular transitions)
        :param rounded_to: Rounded
        :param smooth_act_half_window: Half window to smooth activated values
        :param smooth_ifpl_half_window: Half window to smooth not activated values
        """
        url = urllib.parse.urljoin(base_url, "api/v1/co/") # type: ignore
        super(COWS, self).__init__(conn, url)
        headers = {'Accept': 'application/json'}
        options = []
        if anticipation:
            options.append("anticipation=%d%%20%s" % (anticipation, "min"))
        if average_over_peak:
            options.append("average-over-peak=%f" % (average_over_peak,))
        if instantaneous_over_peak:
            options.append("instantaneous-over-peak=%d" % (instantaneous_over_peak,))
        if minimum_distinct_peak:
            options.append("minimum-distinct-peak=%d%%20%s" % (minimum_distinct_peak, "min"))
        if minimum_overload_time:
            options.append("minimum-overload-time=%d%%20%s" % (minimum_overload_time, "min"))
        if minimum_sector_time:
            options.append("minimum-sector-time=%d%%20%s" % (minimum_sector_time, "min"))
        if overload_extra:
            options.append("overload-extra=%d%%20%s" % (overload_extra, "min"))
        if rating_threshold:
            options.append("rating-threshold=%f" % (rating_threshold,))
        if rounded_to:
            options.append("rounded-to=%d%%20%s" % (rounded_to, "min"))
        if smooth_act_half_window:
            options.append("smooth-act-half-window=%d" % (smooth_act_half_window,))
        if smooth_ifpl_half_window:
            options.append("smooth-ifpl-half-window=%d" % (smooth_ifpl_half_window,))
        url = "init/%s?%s" % (scn_id, "&".join(options))
        self.id = self.put(url, headers=headers)

    def __del__(self):
        self.delete("%s" % (self.id,))

    def set_black_list(self, bl : list[BlackListElement]):
        headers = {'Content-Type': 'application/json'}
        data = BlackListElement.schema().dumps(bl, many=True) # type: ignore
        self.put("%s/blacklist" % (self.id,), data=data, headers=headers)

    def get_black_list(self):
        headers = {'Accept': 'application/json'}
        response = self.get("%s/blacklist" % (self.id,), headers=headers)
        return json.loads(response)

    def set_white_list(self, wl : list[WhiteListElement]):
        headers = {'Content-Type': 'application/json'}
        data = WhiteListElement.schema().dumps(wl, many=True) # type: ignore
        self.put("%s/whitelist" % (self.id,), data=data, headers=headers)

    def get_white_list(self):
        headers = {'Accept': 'application/json'}
        response = self.get("%s/whitelist" % (self.id,), headers=headers)
        return json.loads(response)

    def set_apex_definitions(self, apex):
        headers = {'Content-Type': 'application/json'}
        self.put("%s/apex-definitions" % (self.id,), data=json.dumps(apex), headers=headers)

    def overloaded_periods(self) -> list[OverloadedPeriod]:
        headers = {'Content-Type': 'application/json'}
        response = self.get("%s/overloadedPeriods" % (self.id, ), headers=headers)
        return [OverloadedPeriod.from_json(json.dumps(d)) for d in json.loads(response)] # type: ignore

    def popular_path(self):
        """Get popular path"""
        headers = {'Accept': 'application/json'}
        url = "%s/popularPath" % (self.id,)
        response = self.get(url, headers=headers)
        return json.loads(response)
    
    def propose_collapse(self, wef, unt, n):
        """Propose collapsing"""
        headers = {'Accept': 'application/json'}
        url = "%s/proposeCollapse?wef=%s&unt=%s&n=%d" % (self.id, wef.strftime(COWS.PERIOD_FORMAT), unt.strftime(COWS.PERIOD_FORMAT), n)
        response = self.get(url, headers=headers)
        return ShouldCollapse.schema().loads(response) # type: ignore
    
    def center_hotspots(self, delta_uceso_ucesa=None) -> CenterHotSpots:
        headers = {'Accept': 'application/json'}
        options = []
        if delta_uceso_ucesa:
            options.append("delta-uceso-ucesa=%d" % (delta_uceso_ucesa,))
        end_of_url = "?" + "&".join(options) if options else ""
        url = "%s/chs%s" % (self.id, end_of_url)
        response = self.get(url, headers=headers)
        return CenterHotSpots.schema().loads(response) # type: ignore
    
    def optimize(self, wef: datetime.datetime, unt: datetime.datetime, nb_solutions: int = 0, nb_positions: int = 0) -> list[SectorConfigurationSolution]:
        headers = {'Accept': 'application/json'}
        options = []
        options.append("wef=%s" % (wef.strftime(COWS.PERIOD_FORMAT),))
        options.append("unt=%s" % (unt.strftime(COWS.PERIOD_FORMAT),))
        if nb_solutions:
            options.append("nbSolutions=%d" % (nb_solutions,))
        if nb_positions:
            options.append("nbPositions=%d" % (nb_positions,))
        url = "%s/optimize?%s" % (self.id, "&".join(options))
        response = self.get(url, headers=headers)
        return [SectorConfigurationSolution.from_json(json.dumps(d)) for d in json.loads(response)] # type: ignore
    
    def update(self, update_monitoring):
        """Update the scenario optimizer"""
        headers = {'Accept': 'application/json'}
        url = "%s/update?updateMonitoring=%s" % (self.id, 'true' if update_monitoring else 'false')
        self.put(url, headers=headers)
