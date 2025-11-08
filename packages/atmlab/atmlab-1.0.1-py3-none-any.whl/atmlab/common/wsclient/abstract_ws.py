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

import time
import urllib
from http.client import HTTPException


class AbstractWS(object):
    ACCEPTED_HTTP_CODES = [200, 201, 204]

    def __init__(self, factory_conn, base_url, verbose=False):
        self.factory_conn = factory_conn
        self.base_url = base_url
        self.http = self.factory_conn.get_connection()
        self.verbose = self.factory_conn.verbose

    def get_factory_conn(self):
        return self.factory_conn

    def get_response(self, method, url, **kwargs):

        # Prepare the request
        headers = kwargs.get('headers', {})
        headers['Authorization'] = 'Bearer ' + self.factory_conn.get_token()
        kwargs['headers'] = headers
        full_url = urllib.parse.urljoin(self.base_url, url)

        # Print the cURL command
        if self.verbose:
            # print(method + ' ' + full_url)
            curl_command_line = ["curl", "-k", "-X", method, "'" + full_url + "'"]
            for header, value in headers.items():
                curl_command_line.append("-H")
                curl_command_line.append("'" + header + ": " + value + "'")
            if 'body' in kwargs and kwargs['body']:
                curl_command_line.append("-d")
                # curl_command_line.append("'" + kwargs['body'] + "'")
            print(" ".join(curl_command_line))
            t0 = time.time()

        # Do the request
        r = self.http.request(method, full_url, **kwargs)

        # Print the spent time
        if self.verbose:
            print(time.time() - t0, 's')

        # Process the response
        if r.status in AbstractWS.ACCEPTED_HTTP_CODES:
            return r
        else:
             raise HTTPException("%s: %d\n%s" % (full_url, r.status, r.data))

    def get(self, url, **kwargs):
        return self.get_response('GET', url, **kwargs).data.decode('utf-8')

    def post(self, url, data=None, **kwargs):
        return self.get_response('POST', url, body=data, **kwargs).data.decode('utf-8')

    def put(self, url, data=None, **kwargs):
        return self.get_response('PUT', url, body=data, **kwargs).data.decode('utf-8')

    def delete(self, url, **kwargs):
        return self.get_response('DELETE', url, **kwargs)
