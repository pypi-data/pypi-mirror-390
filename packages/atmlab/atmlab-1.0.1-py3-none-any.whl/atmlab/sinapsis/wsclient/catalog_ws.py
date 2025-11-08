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

import json
import urllib

from atmlab.common.wsclient.abstract_ws import AbstractWS


class CatalogWS(AbstractWS):

    def __init__(self, conn, base_url, tv_set_id, catalog_name):
        url = urllib.parse.urljoin(base_url, "api/v1/catalogs/%s/%s/" % (tv_set_id, catalog_name))
        super(CatalogWS, self).__init__(conn, url)

    def get_otmv(self, tv_id):
        """Get OTMV for a given TV"""
        headers = {'Accept': 'application/json'}
        url = "otmv/%s" % (tv_id,)
        response = self.get(url, headers=headers)
        return json.loads(response)
