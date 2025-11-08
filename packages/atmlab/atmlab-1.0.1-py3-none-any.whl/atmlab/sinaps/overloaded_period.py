import dataclasses_json
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from abc import ABC

from atmlab.common.wsclient.dataclasses_helpers import datetime_metadata

import datetime


@dataclass_json
@dataclass
class OverloadedPeriod(ABC):
    tvId: str
    wef: datetime.datetime = field(metadata=datetime_metadata(field_name='wef', format='%Y-%m-%d %H:%M'))
    unt: datetime.datetime = field(metadata=datetime_metadata(field_name='unt', format='%Y-%m-%d %H:%M'))
    # unt: datetime.datetime | None = field(default=None, metadata=datetime_metadata(field_name='unt', format='%Y-%m-%d %H:%M'))
