# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 ONERA <Judicael.Bedouet@onera.fr>
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

import urllib

from atmlab.common.wsclient.abstract_ws import AbstractWS
from atmlab.common.wsclient.json_helpers import to_simple_namespace

from ..uceso import Uceso

class UcesoWS(AbstractWS):

    def __init__(self, scn_id, conn, base_url, end_of_url):
        url = urllib.parse.urljoin(base_url, "api/v1/uceso/")
        super(UcesoWS, self).__init__(conn, url)
        self.this_base_url = base_url
    
    def post_uceso(self, uceso):
        headers = {'Content-Type': 'application/json'}
        data = Uceso.schema().dumps(uceso)
        self.put("", data=data, headers=headers)
    