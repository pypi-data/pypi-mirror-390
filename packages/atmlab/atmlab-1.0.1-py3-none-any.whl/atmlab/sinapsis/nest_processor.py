#!/usr/bin/python3

# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, 2023, 2025 ONERA <Judicael.Bedouet@onera.fr>
#
# This file is part of PySINAPS.
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

import csv
import os

from atmlab.common.wsclient.configuration import Configuration
from atmlab.sinapsis.wsclient.scenario_factory import ScenarioFactory


class NestProcessor(object):

    def __init__(self, factory: ScenarioFactory, conf: Configuration) -> None:
        self.__factory = factory
        self.__conf = conf

    def import_nest(self, nest_filepath) -> str:

        print('Import NEST file ' + nest_filepath)
        nest_basename = os.path.splitext(os.path.basename(nest_filepath))[0]

        # Read the beginning of the file and find the header line
        index_of_date : int = -1
        fieldnames = None
        nb_header_lines = 0
        with open(nest_filepath, 'r', newline='') as f:
            for line in f:
                line = line.rstrip()
                words = line.split(";")
                for date in ["Date", "date"]:
                    try:
                        index_of_date = words.index(date)
                        fieldnames = line
                    except ValueError:
                        pass
                nb_header_lines += 1
                if fieldnames is not None:
                    break

        if fieldnames is None:
            print('Can not find a line with Date or date')
            exit(-1)

        tv_set_id = self.__conf.tv_set_id
        center_tv = self.__conf.data['center_tv']
        overloading_catalog = self.__conf.data['overloading_catalog'] if 'overloading_catalog' in self.__conf.data else None

        scn_id = self.__factory.init_nest_scenario(tv_set_id, center_tv, overloading_catalog)
        print("New NEST scenario created: %s" % (scn_id,))
        print()

        # Reopen the file and send each day separately.
        with open(nest_filepath, 'r', newline='') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
            # Skip the first lines
            for i in range(0, nb_header_lines):
                next(reader)
            # Now, read the file
            day_rows = [fieldnames]
            current_date = None
            for row in reader:
                date = row[index_of_date]
                if current_date is None:  # First line
                    current_date = date
                if date != current_date:
                    # Process the previous day
                    self.__process_rows(scn_id, nest_basename, current_date, day_rows)
                    day_rows.clear()
                    day_rows.append(fieldnames)
                    current_date = date
                day_rows.append(';'.join(row))
        # Process the last day
        self.__process_rows(scn_id, nest_basename, current_date, day_rows)

        return scn_id

    # Send one day of data to the server.
    def __process_rows(self, scn_id, nest_basename, day, rows) -> None:
        print('Sending', day, '...')
        data = '\r\n'.join(rows)
        name = nest_basename + '_' + day
        self.__factory.add_to_nest_scenario(scn_id, name, data)
