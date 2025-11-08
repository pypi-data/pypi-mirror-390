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

import os
import yaml
import urllib3

from atmlab.common.wsclient.server_url_connection import ServerURLConnection


class Configuration(object):

    def __init__(self, specific_yaml_filename=None, argv=[]):
        ''' Initialize the ATMLab configuration.
        Configuration specific to this run can be set through a YAML file or a list of arguments,
        for example, passed from the command-line.
        The provided arguments override any previously defined parameters, except for those explicitly defined in the TV set file.
        
        Args:
            specific_yaml_filename (str, optional): A YAML file that contains the configuration specific to this run.
            argv (list[str], optional): A list of configuration arguments specific to this run.
        '''

        data = {}

        print()
        # Read the YAML configuration files
        for filename in ['common.yaml', 'user.yaml', specific_yaml_filename]:
            if filename:
                print('Loading', filename)
                with open(filename) as f:
                    data.update(yaml.load(f, Loader=yaml.FullLoader))

        # Seek a TV Set ID argument
        if 'tv_set_id' in argv:
            data['tv_set_id'] = argv['tv_set_id']
        
        # Read the TV Set ID
        self.tv_set_id = data['tv_set_id'] if 'tv_set_id' in data else None
        self.tv_set_location = data['tv_set_location'] if 'tv_set_location' in data else './'

        # Read the TV Set ID configuration file
        if self.tv_set_id:
            tv_set_filename = os.path.join(self.tv_set_location, self.tv_set_id + '.yaml')
            print('Loading', tv_set_filename)
            with open(tv_set_filename) as f:
                data.update(yaml.load(f, Loader=yaml.FullLoader))
        print()

        # Read the configuration from the specific arguments
        if argv:
            print('Set the specific arguments')
            data.update(argv)
        
        self.username = data['username']
        self.password = data['password']
        self.proxies = data['proxies']
        self.verbose = data['verbose'] if 'verbose' in data else False
        self.timeout_connect = float(data['timeout']['connect'])
        self.timeout_read = float(data['timeout']['read'])
        self.timeout = urllib3.Timeout(connect=self.timeout_connect, read=self.timeout_read)
        services = data['services']
        self.auth_url = services['auth'] if 'auth' in services else None
        self.emissions_url = services['emissions'] if 'emissions' in services else None
        self.jfs_url = services['jfs'] if 'jfs' in services else None
        self.sinapsis_url = services['sinapsis'] if 'sinapsis' in services else None
        self.sinaps_url = services['sinaps'] if 'sinaps' in services else None
        self.black_list = data['blacklist'] if 'blacklist' in data else []
        self.white_list = data['whitelist'] if 'whitelist' in data else []
        self.overloading_catalog = data['overloading_catalog'] if 'overloading_catalog' in data else None
        if 'sinaps' in data:
            self.average_over_peak = data["sinaps"]["average_over_peak"]
            self.instantaneous_over_peak = data["sinaps"]["instantaneous_over_peak"]
            self.minimum_distinct_peak = data["sinaps"]["minimum_distinct_peak"]
            self.minimum_overload_time = data["sinaps"]["minimum_overload_time"]
            self.minimum_sector_time = data["sinaps"]["minimum_sector_time"]
            self.rating_threshold = data["sinaps"]["rating_threshold"]
            self.rounded_to = data["sinaps"]["rounded_to"] if 'rounded_to' in data['sinaps'] else 0
            self.optimise_uceso = bool(data["sinaps"]["optimise_uceso"]) if 'optimise_uceso' in data["sinaps"] else False
        if 'smooth' in data:
            self.smooth_act_half_window = data["smooth"]["act"]
            self.smooth_ifpl_half_window = data["smooth"]["ifpl"]
        if 'output' in data:
            self.output_csv = bool(data["output"]["csv"])
            self.output_png = bool(data["output"]["png"])
            self.output_html = bool(data["output"]["html"]) if 'html' in data['output'] else False
            if 'includes' in data['output']:
                self.output_includes = data["output"]["includes"]
            else:
                self.output_includes = []
        self.apex = data['apex'] if 'apex' in data else []
        self.data = data
        if 'compression' in data:
            self.nest_compression = bool(data['compression']['nest']['enabled']) if 'nest' in data['compression'] else False
        else:
            self.nest_compression = False

    def connection(self):
        return ServerURLConnection(self.auth_url, self.username, self.password, self.proxies, self.timeout, verbose=self.verbose)
