import dataclasses_json
from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase

from abc import ABC
from typing import List, Union

from atmlab.common.wsclient.dataclasses_helpers import datetime_metadata

import datetime


@dataclass_json
@dataclass
class BlackListElement(ABC):
    tvId: str
    begin: datetime.datetime | None = field(default=None, metadata=datetime_metadata(field_name='from', format='%Y-%m-%d %H:%M'))
    end: datetime.datetime | None = field(default=None, metadata=datetime_metadata(field_name='to', format='%Y-%m-%d %H:%M'))


@dataclass_json
@dataclass
class WhiteListElement(ABC):
    tvId: str
    strict: bool
    begin: datetime.datetime | None = field(default=None, metadata=datetime_metadata(field_name='from', format='%Y-%m-%d %H:%M'))
    end: datetime.datetime | None = field(default=None, metadata=datetime_metadata(field_name='to', format='%Y-%m-%d %H:%M'))
