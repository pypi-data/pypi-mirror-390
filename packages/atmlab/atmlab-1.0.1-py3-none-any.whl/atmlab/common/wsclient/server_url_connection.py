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
import json
import urllib
from http.client import HTTPException

import certifi
import jwt
import urllib3


class ServerURLConnection(object):

    def __init__(self, base_url, username, password, proxies, timeout, verbose=False):
        
        if not timeout:
            timeout = urllib3.Timeout()

        self.base_url = base_url
        self.username = username
        self.password = password
        self.verbose = verbose
        self.token = None
        
        self.proxies = proxies
        if not proxies:
            self.proxies = {'http': '', 'https': ''}
        
        if self.proxies['https']:
            self.http = urllib3.ProxyManager(proxies['https'], cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),
                                             timeout=timeout)
        else:
            self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), timeout=timeout)

    def get_proxies(self):
        return self.proxies

    def get_connection(self):
        return self.http

    def set_token(self, token):
        self.token = token

    def get_token(self):
        """Get an authentication token"""
        if self.token is None:
            self.__renew_token()
        else:
            decoded = jwt.decode(self.token, verify=False, algorithms='HS256', options={"verify_signature": False})
            exp = datetime.datetime.utcfromtimestamp(decoded['exp'])
            now = datetime.datetime.utcnow()
            # Regenerate token two minutes before its expiration
            if now + datetime.timedelta(minutes=2) > exp:
                self.__renew_token()
        return self.token

    def __renew_token(self):
        """Query a new token"""
        url = urllib.parse.urljoin(self.base_url, 'auth/login')
        data = json.dumps({'username': self.username, 'password': self.password}).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        r = self.http.request('POST', url, body=data, headers=headers)
        if r.status == 200:
            print('Generate a new token')
            self.token = r.data.decode('utf-8')
        else:
            raise HTTPException('Can not renew token: %d\n%s' % (r.status, r.data))
