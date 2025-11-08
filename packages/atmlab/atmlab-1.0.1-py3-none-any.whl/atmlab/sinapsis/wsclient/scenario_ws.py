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

from atmlab.sinapsis.uceso import UC

from .catalog_ws import CatalogWS
from atmlab.common.wsclient.abstract_ws import AbstractWS
from atmlab.common.wsclient.json_helpers import to_simple_namespace
from typing import List


class ScenarioWS(AbstractWS):

    def __init__(self, scn_id, conn, base_url, end_of_url):
        url = urllib.parse.urljoin(base_url, "api/v1/scenarios/")
        super(ScenarioWS, self).__init__(conn, url)
        self.this_base_url = base_url
        if scn_id is None:
            headers = {'Accept': 'application/json'}
            self.scn_id = self.get(end_of_url, headers=headers)
        else:
            self.scn_id = scn_id

    def set_apex_definitions(self, apex):
        if apex:
            headers = {'Content-Type': 'application/json'}
            self.put("%s/apexDefinitions" % (self.scn_id,), data=json.dumps(apex), headers=headers)

    def advance(self, t):
        """Advance"""
        headers = {'Accept': 'application/json'}
        t_s = t.strftime("%Y-%m-%dT%H:%M:%SZ").replace(' ', '%20')
        url = "%s/advance?t=%s" % (self.scn_id, t_s)
        response = self.put(url, headers=headers)
        return json.loads(response)

    def copy_occupancy_img_to(self, to, tv_id, period=None, duration=None, width=1024, height=640, smooth_act_half_window=0, smooth_ifpl_half_window=0):
        """Create an image file with occupancy for tv_id between wef and unt"""
        headers = {'Accept': 'image/png'}
        options = ["width=%d" % (width,), "height=%d" % (height,)]
        if period:
            if period['wef']:
                options.append("wef=" + period['wef'].replace(' ', '%20'))
            if period['unt']:
                options.append("unt=" + period['unt'].replace(' ', '%20'))
        if duration:
            options.append("duration=" + duration)
        if smooth_act_half_window > 0:
            options.append("smooth-act-half-window=%d" % (smooth_act_half_window,))
        if smooth_ifpl_half_window > 0:
            options.append("smooth-ifpl-half-window=%d" % (smooth_ifpl_half_window,))
        url = "%s/occupancies/image/%s?%s" % (self.scn_id, tv_id, "&".join(options))
        response = self.get_response('GET', url, headers=headers)
        to.write(response.data)

    def get_catalog_name(self):
        """Returns the corresponding catalog"""
        headers = {'Accept': 'application/json'}
        url = "%s/catalogName" % (self.scn_id,)
        return self.get(url, headers=headers)

    def get_tv_set_id(self):
        """Returns the corresponding TV set id"""
        headers = {'Accept': 'application/json'}
        url = "%s/tvSetId" % (self.scn_id,)
        return self.get(url, headers=headers)

    def get_catalog(self):
        """Returns the corresponding catalog"""
        catalog_name = self.get_catalog_name()
        tv_set_id = self.get_tv_set_id()
        return CatalogWS(self.factory_conn, self.this_base_url, tv_set_id, catalog_name)

    def get_current_time(self):
        """Returns the current time"""
        headers = {'Accept': 'application/json'}
        url = "%s/currentTime" % (self.scn_id,)
        response = self.get(url, headers=headers)
        return datetime.datetime.strptime(response, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=datetime.timezone.utc)

    def get_period(self):
        """Returns the current period"""
        headers = {'Accept': 'application/json'}
        url = "%s/period" % (self.scn_id,)
        response = self.get(url, headers=headers)
        return json.loads(response)

    def get_status(self):
        """Returns the status of this scenario"""
        headers = {'Accept': 'application/json'}
        url = "%s/status" % (self.scn_id,)
        response = self.get(url, headers=headers)
        return json.loads(response)
    
    def get_uceso_plan(self) -> List[UC]:
        """Returns the UCESO plan"""
        headers = {'Accept': 'application/json'}
        url = "%s/uceso" % (self.scn_id,)
        response = self.get(url, headers=headers)
        return [UC.from_dict(e) for e in json.loads(response)]
        
    def get_current_configuration(self, convert_to_airspace=True, default_if_needed=False):
        """Returns the current configuration"""
        headers = {'Accept': 'application/json'}
        url = "%s/currentConfiguration?convertToAirspace=%s&defaultIfNeeded=%s"
        url = url % (self.scn_id, 'true' if convert_to_airspace else "false", "true" if default_if_needed else "false")
        response = self.get(url, headers=headers)
        return json.loads(response)

    def get_flights(self, tv_id, period=None, duration=None):
        """Returns flights for the given TV"""
        headers = {'Accept': 'application/json'}
        options = []
        if period:
            if period['wef']:
                options.append("wef=" + period['wef'].replace(' ', '%20'))
            if period['unt']:
                options.append("unt=" + period['unt'].replace(' ', '%20'))
        if duration:
            options.append("duration=" + duration)
        url = "%s/flights/%s?%s" % (self.scn_id, tv_id, "&".join(options))
        response = self.get(url, headers=headers)
        obj = to_simple_namespace(response)
        return obj.flights

    def get_occupancy(self, tv_id, period=None, duration=None, smooth_act_half_window=0, smooth_ifpl_half_window=0):
        """Returns occupancy for the given TV"""
        headers = {'Accept': 'application/json'}
        options = []
        if period:
            if period['wef']:
                options.append("wef=" + period['wef'].replace(' ', '%20'))
            if period['unt']:
                options.append("unt=" + period['unt'].replace(' ', '%20'))
        if duration:
            options.append("duration=" + duration)
        if smooth_act_half_window > 0:
            options.append("smooth-act-half-window=%d" % (smooth_act_half_window,))
        if smooth_ifpl_half_window > 0:
            options.append("smooth-ifpl-half-window=%d" % (smooth_ifpl_half_window,))
        url = "%s/occupancies/%s?%s" % (self.scn_id, tv_id, "&".join(options))
        response = self.get(url, headers=headers)
        return json.loads(response)
    
    def occupancy_counts(self, tv_id, period=None, duration=None, smooth_act_half_window=0, smooth_ifpl_half_window=0, include_otmv_values=False):
        headers = {'Accept': 'application/json'}
        options = []
        if period:
            if period['wef']:
                options.append("wef=" + period['wef'].replace(' ', '%20'))
            if period['unt']:
                options.append("unt=" + period['unt'].replace(' ', '%20'))
        if duration:
            options.append("duration=" + duration)
        if smooth_act_half_window > 0:
            options.append("smoothActHalfWindow=%d" % (smooth_act_half_window,))
        if smooth_ifpl_half_window > 0:
            options.append("smoothIfplHalfWindow=%d" % (smooth_ifpl_half_window,))
        if include_otmv_values:
            options.append('includeOtmvValues=true')
        url = "%s/occupancy-counts/%s?%s" % (self.scn_id, tv_id, "&".join(options))
        response = self.get(url, headers=headers)
        return json.loads(response)
    
    def reset(self):
        """Reset"""
        headers = {'Accept': 'application/json'}
        url = "%s/reset" % (self.scn_id,)
        response = self.put(url, headers=headers)
        return json.loads(response)
