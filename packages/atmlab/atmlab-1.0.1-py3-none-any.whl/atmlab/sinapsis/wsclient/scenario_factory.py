# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, 2023 ONERA <Judicael.Bedouet@onera.fr>
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
import json
import urllib
import gzip

from atmlab.common.wsclient.abstract_ws import AbstractWS
from atmlab.sinapsis.wsclient.scenario_ws import ScenarioWS


class ScenarioFactory(AbstractWS):

    def __init__(self, conn, base_url, compress=False):
        url = urllib.parse.urljoin(base_url, "api/v1/scenarios/")
        super().__init__(conn, url)
        self.original_base_url = base_url
        self.compress = compress

    def init_nest_scenario(self, tv_set_id, center_tv, overloading_catalog=None):
        """Init a NEST scenario"""
        headers = {'Accept': 'application/json'}
        url = "initFromNEST?tvSetId=%s&centerTv=%s" % (tv_set_id, center_tv)
        if overloading_catalog:
            url += "&overloadingCatalog=%s" % (overloading_catalog,)
        return self.post(url, headers=headers)

    def add_to_nest_scenario(self, scn_id, name, input):
        """Complete a NEST scenario"""
        headers = {'Content-Type': 'text/csv', 'Accept': 'application/json'}
        url = "addToNestScenario?scnId={}&name={}".format(scn_id, name)
        if self.compress:
            headers['Content-Encoding'] = 'gzip'
            print("Compressing...", end="", flush=True)
            encoded_input = input.encode()
            data = gzip.compress(encoded_input)
            compress_rate = 100 * len(data) / len(encoded_input)
            print(" %.0f %%\r" % (compress_rate,))
        else:
            data = input
        self.put(url, data=data, headers=headers)

    def init_replay_scenario(self, tv_set_id, start, catalog=None):
        headers = {'Content-Type': 'text/csv', 'Accept': 'application/json'}
        url = "initReplayScenario?tvSetId=%s&start=%s"
        url = url % (tv_set_id, start.strftime('%Y-%m-%d %H:%M').replace(' ', '%20'))
        if catalog:
            url = url + "&catalog=%s" % catalog
        scn_id = self.post(url, headers=headers)
        return scn_id

    def get_predict_scenario(self, tv_set_id, date):
        """Init a PREDICT scenario"""
        url = "getPredictScenario?tv-set-id=%s&day=%s" % (tv_set_id, date.strftime('%Y-%m-%d'))
        scn_id = self.get(url)
        return scn_id

    def get_scenarios(self, parent_id):
        """Get the different sub scenarios of a scenario"""
        headers = {'Accept': 'application/json'}
        url = "getScenarios?parentId=%s" % (parent_id,)
        ids = self.get(url, headers=headers)
        mapping = json.loads(ids)
        sub_scenarios = {}
        for date_s, scn_id in mapping.items():
            d = datetime.datetime.strptime(date_s, "%Y-%m-%dT%H:%M:%SZ")
            sub_scenarios[d] = scn_id
        return sub_scenarios

    def init_scenario(self, scn_id, catalog=None):
        """Optional operation to init a scenario. May be useful to update the catalog."""
        options = []
        if catalog:
            options.append("catalog=" + catalog)
        url = "%s/init?%s" % (scn_id, "&".join(options))
        self.put(url)

    def release_scenario(self, scn_id):
        self.delete(scn_id)

    def get_scenario(self, scn_id):
        return ScenarioWS(scn_id, self.get_factory_conn(), self.original_base_url, None)
