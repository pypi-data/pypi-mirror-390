import dataclasses_json
from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase

from atmlab.common.wsclient.dataclasses_helpers import datetime_metadata, quantity_metadata

import datetime

@dataclass_json
@dataclass
class CenterHotSpot(object):
    begin: datetime.datetime = field(metadata=datetime_metadata(field_name='from'))
    end: datetime.datetime = field(metadata=datetime_metadata(field_name='to'))
    delta: int
    ucesa: int
    uceso: int
    id: str = field(default=None, metadata=config(field_name=":id"))
    type: str = field(default="CenterHotSpot", metadata=config(field_name=":type"))

@dataclass_json
@dataclass
class CenterHotSpots(object):
    wef: datetime.datetime = field(metadata=datetime_metadata(field_name='from'))
    unt: datetime.datetime = field(metadata=datetime_metadata(field_name='to'))
    the_hotspots: list[CenterHotSpot] = field(default_factory=list, metadata=config(field_name="theHotSpots"))
    id: str = field(default=None, metadata=config(field_name=":id"))
    type: str = field(default="CenterHotSpots", metadata=config(field_name=":type"))
