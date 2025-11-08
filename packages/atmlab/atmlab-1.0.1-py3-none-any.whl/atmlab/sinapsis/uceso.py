# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 ONERA <Judicael.Bedouet@onera.fr>
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
import dataclasses_json
from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json
import datetime
from marshmallow import fields
from typing import List, Union

from atmlab.common.wsclient.dataclasses_helpers import datetime_metadata, quantity_metadata
from gamme.units import Quantity


@dataclass_json
@dataclass
class UC(object):
    nb: int
    begin: datetime.datetime = field(metadata=datetime_metadata(field_name='from'))
    end: datetime.datetime = field(metadata=datetime_metadata(field_name='to'))
    id: str = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='UCESO', metadata=config(field_name=':type'))

def read_ucesos(filename) -> List[UC]:
    with open(filename, 'r') as f:
        data = json.load(f)
    return [UC.schema().load(e) for e in data]

def write_ucesos(ucesos: List[UC], filename):
    with open(filename, 'w') as f:
        dict = UC.schema().dump(ucesos, many=True)
        json.dump(dict, f, indent=4)

@dataclass_json
@dataclass
class Uceso(object):
    tv_set_id: str = field(metadata=config(field_name='tvSetId'))
    day: datetime.datetime = field(metadata=datetime_metadata())
    plan : list[UC]
    type: str = field(default='UCESO', metadata=config(field_name=':type'))
