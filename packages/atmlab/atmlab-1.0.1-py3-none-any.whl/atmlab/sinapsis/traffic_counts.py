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

from enum import Enum, unique
from typing import Any, Dict, Generator, List
from atmlab.sinapsis.otmv import OTMV


@unique
class TrafficType(Enum):
    DEMAND = 0
    REGULATED_DEMAND = 1
    LOAD = 2
    WHAT_IF = 3


@unique
class SubTotalTrafficCountsType(Enum):
    ATC_ACTIVATED = 0,
    TACT_ACTIVATED_WITHOUT_FSA = 1,
    IFPL = 2,
    RPL = 3,
    PFD = 4,
    SUSPENDED = 5,
    TACT_ACTIVATED_WITH_FSA = 6


class TrafficCountItem(object):

    def __init__(
            self,
            total_counts=0,
            atc_activated=0,
            ifpl=0,
            mfd=0,
            pfd=0,
            rpl=0,
            suspended=0,
            tact_activated_with_fsa=0,
            tact_activated_without_fsa=0,
            terminated=0,
            otmv=None
    ):
        self.total_counts = total_counts
        self.atc_activated = atc_activated
        self.ifpl = ifpl
        self.mfd = mfd
        self.pfd = pfd
        self.rpl = rpl
        self.suspended = suspended
        self.tact_activated_with_fsa = tact_activated_with_fsa
        self.tact_activated_without_fsa = tact_activated_without_fsa
        self.terminated = terminated
        self.otmv = otmv
    
    def value(self, subtype: SubTotalTrafficCountsType) -> int:
        if subtype == SubTotalTrafficCountsType.ATC_ACTIVATED:
            return self.atc_activated
        elif subtype == SubTotalTrafficCountsType.TACT_ACTIVATED_WITHOUT_FSA:
            return self.tact_activated_without_fsa
        elif subtype == SubTotalTrafficCountsType.IFPL:
            return self.ifpl
        elif subtype == SubTotalTrafficCountsType.RPL:
            return self.rpl
        elif subtype == SubTotalTrafficCountsType.PFD:
            return self.pfd
        elif subtype == SubTotalTrafficCountsType.SUSPENDED:
            return self.suspended
        elif subtype == SubTotalTrafficCountsType.TACT_ACTIVATED_WITH_FSA:
            return self.tact_activated_with_fsa


class TrafficCounts(object):

    def __init__(self, tv, wef: datetime.datetime, unt: datetime.datetime, step: datetime.timedelta, duration: datetime.timedelta, items: list[TrafficCountItem]):
        self.tv = tv
        self.wef = wef
        self.unt = unt
        self.step = step
        self.duration = duration
        self.__items = items
        assert (self.unt - self.wef).total_seconds() // 60 == len(self.__items), "[%s %s]: %d" % (self.wef, self.unt, len(self.__items))

    def index_of(self, t) -> int:
        # print(self.wef, " ¤ ", t, " ¤ ", self.unt)
        assert self.wef <= t <= self.unt, "[%s] %s not in [%s..%s]" % (self.tv, t, self.wef, self.unt)
        diff = t - self.wef
        index = diff.total_seconds() // self.step.total_seconds()
        assert 0 <= index <= len(self.__items), "[%s] %d not in [0..%d]" % (self.tv, index, len(self.__items))
        return int(index)

    def time_length(self) -> datetime.timedelta:
        return self.unt - self.wef
    
    def item(self, t) -> TrafficCountItem:
        index = self.index_of(t)
        assert 0 <= index < len(self.__items), "%d not in [0..%d[" % (index, len(self.__items))
        return self.__items[index]

    def items(self) -> Generator[tuple[datetime.datetime, TrafficCountItem], Any, None]:
        for i in range(0, len(self.__items)):
            t = self.wef + i * datetime.timedelta(seconds=self.step.seconds)
            yield t, self.item(t)

    def sub_counts(self, fr, to) -> "TrafficCounts":
        return TrafficCounts(self.tv, fr, to, self.step, self.duration, self.__items[self.index_of(fr):self.index_of(to)])

    @staticmethod
    def convert(tv, json) -> Dict[TrafficType, "TrafficCounts"]:

        dtf = '%Y-%m-%d %H:%M'
        etw = json['effectiveTrafficWindow']
        wef = datetime.datetime.strptime(etw['wef'], dtf).replace(tzinfo=datetime.timezone.utc)

        m : Dict[str, List[TrafficCountItem]]= {}

        items = json['counts']['item']
        if len(items) > 1:
            fst = datetime.datetime.strptime(items[0]['key']['wef'], dtf).replace(tzinfo=datetime.timezone.utc)
            snd = datetime.datetime.strptime(items[1]['key']['wef'], dtf).replace(tzinfo=datetime.timezone.utc)
            fst_unt = datetime.datetime.strptime(items[0]['key']['unt'], dtf).replace(tzinfo=datetime.timezone.utc)
            step, duration = snd - fst, fst_unt - fst
        else:
            step, duration = datetime.timedelta(minutes=1), datetime.timedelta(minutes=1)

        unt = datetime.datetime.strptime(etw['unt'], dtf).replace(tzinfo=datetime.timezone.utc)
        unt = unt - duration + datetime.timedelta(minutes=1)

        for item1 in items:
            for item2 in item1['value']['item']:
                traffic_type = item2['key']
                i = TrafficCountItem()
                i.total_counts = int(item2['value']['totalCounts'])
                for item3 in item2['value']['subTotalsCounts']['item']:
                    k = item3['key']
                    v = item3['value']
                    if k == 'ATC_ACTIVATED':
                        i.atc_activated = v
                    elif k == 'IFPL':
                        i.ifpl = v
                    elif k == 'MFD':
                        i.mfd = v
                    elif k == 'PFD':
                        i.pfd = v
                    elif k == 'RPL':
                        i.rpl = v
                    elif k == 'SUSPENDED':
                        i.suspended = v
                    elif k == 'TACT_ACTIVATED_WITH_FSA':
                        i.tact_activated_with_fsa = v
                    elif k == 'TACT_ACTIVATED_WITHOUT_FSA':
                        i.tact_activated_without_fsa = v
                    elif k == "TERMINATED":
                        i.terminated = v
                    else:
                        raise RuntimeError('Unknown key: %s' % (k,))

                if traffic_type not in m:
                    m[traffic_type] = []
                m[traffic_type].append(i)

        result : Dict[TrafficType, TrafficCounts] = {}
        for traffic_type, items in m.items():
            result[TrafficType[traffic_type]] = TrafficCounts(tv, wef, unt, step, duration, items)

        return result

    @staticmethod
    def convert2(json, duration=None, step=None) -> Dict[TrafficType, "TrafficCounts"]:

        dtf = '%Y-%m-%d %H:%M'
        
        tv = json['location']

        if not duration:
            duration = _duration_hour_minute(json['duration'])
            duration = datetime.timedelta(minutes=duration)

        if not step:
            step = _duration_hour_minute(json['step'])
            step = datetime.timedelta(minutes=step)

        etw = json['effectiveTrafficWindow']
        wef = datetime.datetime.strptime(etw['wef'], dtf).replace(tzinfo=datetime.timezone.utc)

        m : Dict[str, List[TrafficCountItem]]= {}

        unt = datetime.datetime.strptime(etw['unt'], dtf).replace(tzinfo=datetime.timezone.utc)
        unt = unt - duration + datetime.timedelta(minutes=1)

        for traffic_type, v1 in json['counts'].items():
            for item in v1['items']:
                i = TrafficCountItem()
                i.total_counts = item['totalCounts']
                if 'otmv' in item and item['otmv']:
                    i.otmv = OTMV(sustain=item['otmv']['sustain'], peak=item['otmv']['peak'])
                for k, v in item['subTotalsCounts'].items():
                    if k == 'ATC_ACTIVATED':
                        i.atc_activated = v
                    elif k == 'IFPL':
                        i.ifpl = v
                    elif k == 'MFD':
                        i.mfd = v
                    elif k == 'PFD':
                        i.pfd = v
                    elif k == 'RPL':
                        i.rpl = v
                    elif k == 'SUSPENDED':
                        i.suspended = v
                    elif k == 'TACT_ACTIVATED_WITH_FSA':
                        i.tact_activated_with_fsa = v
                    elif k == 'TACT_ACTIVATED_WITHOUT_FSA':
                        i.tact_activated_without_fsa = v
                    elif k == "TERMINATED":
                        i.terminated = v
                    else:
                        raise RuntimeError('Unknown key: %s' % (k,))

                if traffic_type not in m:
                    m[traffic_type] = []
                m[traffic_type].append(i)

        result : Dict[TrafficType, TrafficCounts] = {}
        for traffic_type, items in m.items():
            result[TrafficType[traffic_type]] = TrafficCounts(tv, wef, unt, step, duration, items)

        return result

def _duration_hour_minute(s) -> int:
    hours = int(s[:2])
    minutes = int(s[2:])
    return hours * 60 + minutes
