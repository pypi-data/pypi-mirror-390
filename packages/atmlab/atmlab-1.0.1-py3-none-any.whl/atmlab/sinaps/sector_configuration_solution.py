import dataclasses_json
from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase

from typing import Dict, List, Type, Union

from atmlab.common.wsclient.dataclasses_helpers import datetime_metadata, quantity_metadata

from gamme.units import Quantity
import datetime
import json


@dataclass_json
@dataclass
class SectorSolutionValues(object):
    overload: float
    # overload_duration: Quantity = field(metadata=quantity_metadata(field_name='overloadDuration'))
    overload_duration: str = field(metadata=config(field_name='overloadDuration'))
    overload_by_duration: float = field(metadata=config(field_name='overloadByDuration'))
    overload_sustain: float = field(metadata=config(field_name='overloadSustain'))
    over_peak: bool = field(metadata=config(field_name='overPeak'))
    max_over_peak: int = field(metadata=config(field_name='maxOverPeak'))
    status: str
    id: str | None = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='SectorSolutionValues', metadata=config(field_name=':type'))


@dataclass_json
@dataclass
class SectorSolution(object):
    the_sector: str = field(metadata=config(field_name='theSector'))
    airspace_id: str = field(metadata=config(field_name='airspaceId'))
    tv_id: str = field(metadata=config(field_name='tvId'))
    values: SectorSolutionValues
    values_before: SectorSolutionValues = field(metadata=config(field_name='valuesBefore'))
    values_after: SectorSolutionValues = field(metadata=config(field_name='valuesAfter'))
    is_splittable: bool = field(metadata=config(field_name='splittable'))
    id: str | None = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='SectorSolution', metadata=config(field_name=':type'))


@dataclass_json
@dataclass
class SectorTransition(object):
    at: datetime.datetime = field(metadata=datetime_metadata())
    popularity: float | None
    type: str = field(metadata=config(field_name=':type'))

@dataclass_json
@dataclass
class Collapsing(SectorTransition):
    tv1: str
    tv2: str
    new_tv: str = field(metadata=config(field_name='newTv'))
    id: str | None = field(default=None, metadata=config(field_name=':id'))

@dataclass_json
@dataclass
class Uncollapsing(SectorTransition):
    old_tv: str = field(metadata=config(field_name='oldTv'))
    tv1: str
    tv2: str
    id: str | None = field(default=None, metadata=config(field_name=':id'))

@dataclass_json
@dataclass
class SectorTransfer(SectorTransition):
    old_tv1: str = field(metadata=config(field_name='oldTv1'))
    old_tv2: str = field(metadata=config(field_name='oldTv2'))
    new_tv1: str = field(metadata=config(field_name='newTv1'))
    new_tv2: str = field(metadata=config(field_name='newTv2'))
    transfert_tv: str = field(metadata=config(field_name='transferTv'))
    id: str | None = field(default=None, metadata=config(field_name=':id'))

SECTOR_TRANSITION_TYPE_MAP: Dict[str, Type[SectorTransition]] = {
    "Collapsing": Collapsing,
    "Uncollapsing": Uncollapsing,
    "SectorTransfer": SectorTransfer
}

def type_of_sector_transition(data: str):
    raw = json.loads(data)
    return SECTOR_TRANSITION_TYPE_MAP.get(raw.get(":type"))

@dataclass_json
@dataclass
class ShouldCollapse(object):
    tv1: str
    tv2: str
    new_tv: str = field(metadata=config(field_name='newTv'))
    overload: float

@dataclass_json
@dataclass
class SectorTransitionSolution(object):
    transition: SectorTransition
    conf: list[str] = field(default_factory=list)
    id: str | None = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='SectorTransitionSolution', metadata=config(field_name=':type'))


@dataclass_json
@dataclass
class SectorTransitionPath(object):
    n: int
    initial_conf : List[str] = field(metadata=config(field_name='initialConf'))
    path_element: List[SectorTransitionSolution] = field(metadata=config(field_name='pathElement'))
    id: str | None = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='SectorTransitionPath', metadata=config(field_name=':type'))


@dataclass_json
@dataclass
class SectorConfigurationSolution(object):
    sector_solution: List[SectorSolution] = field(metadata=config(field_name='sectorSolution'))
    rating: float
    path: SectorTransitionPath
    id: str | None = field(default=None, metadata=config(field_name=':id'))
    type: str = field(default='SectorConfigurationSolution', metadata=config(field_name=':type'))
