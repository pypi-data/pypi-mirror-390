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


import bisect
import csv
import datetime
from typing import Any, Dict, Generator, List, Set


def pairwise(iterable) -> Generator[tuple[Any, Any], Any, None]:
    it = iter(iterable)
    a = next(it, None)
    for b in it:
        yield a, b
        a = b


class Uces(object):

    TRANSITION_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, uces: Dict[datetime.datetime, List[List[str]]]) -> None:
        self._uces = uces
        self.instants = sorted(self._uces)
        self.wef = self.instants[0]
        self.unt = self.instants[-1]
        self._highlight_periods = None
    
    def subset(self, wef: datetime.datetime, unt: datetime.datetime) -> "Uces":
        uces = {}
        if not wef in self.instants:
            uces[wef] = [self.get_conf(wef)]
        uces.update(dict((k, self._uces[k]) for k in self.instants if wef <= k <= unt))
        if not unt in uces:
            uces[unt] = [self.get_conf(unt)]
        return Uces(uces)
    
    def plan(self) -> List[tuple]:
        plan = []
        previous_date = self.wef
        last_conf = None
        for date, confs in self._uces.items():
            conf = confs[-1]
            if last_conf:
                plan.append((previous_date, date, last_conf))
            previous_date = date
            last_conf = conf
        return plan
    
    def events(self):
        events = []
        for c1, c2 in pairwise(self.plan()):
            _, k2, current_conf = c1
            _, _, next_conf = c2
            current_conf = set(current_conf)
            next_conf = set(next_conf)
            diff1 = list(current_conf - next_conf)
            diff2 = list(next_conf - current_conf)
            events.append((k2, diff1, diff2, len(current_conf), len(next_conf)))
        return events

    def get_conf(self, date_of_conf: datetime.datetime) -> List[str]:
        if date_of_conf in self._uces:
            return self._uces[date_of_conf][-1]
        else:
            ind = bisect.bisect(self.instants, date_of_conf)
            if ind > 0:
                return self._uces[self.instants[ind-1]][-1]
            return self._uces[self.instants[ind]][-1]
    
    def get_sectors(self) -> Set[str]:
        sectors = set([])
        for _, confs in self._uces.items():
            for conf in confs:
                sectors.update(conf)
        return sectors

    def get_highlight_periods_of(self, tv_id: str) -> list[tuple[datetime.datetime, datetime.datetime]]:
        return self.get_highlight_periods().get(tv_id, [])

    def get_highlight_periods(self) -> dict[str, list[tuple[datetime.datetime, datetime.datetime]]]:
        
        if self._highlight_periods:
            return self._highlight_periods
        
        self._highlight_periods={}
        
        prev_conf = []
        for date, confs in self._uces.items():
            for conf in confs:
                for s in conf:
                    # We start a new period for each new sector
                    if not s in self._highlight_periods:
                        self._highlight_periods[s] = [(date, None)]
                    elif not s in prev_conf:
                        self._highlight_periods[s].append((date, None))
                for s in prev_conf:
                    # We extend the period of the sectors in the previous configuration
                    # until the current instant
                    begin, _ = self._highlight_periods[s][-1]
                    self._highlight_periods[s][-1] = (begin, date)
                prev_conf = conf
        
        for s in prev_conf:
            begin, _ = self._highlight_periods[s][-1]
            self._highlight_periods[s][-1] = (begin, self.unt)
        
        # Remove null-periods
        self._highlight_periods = {
            key: [(wef, unt) for wef, unt in periods if wef < unt]
            for key, periods in self._highlight_periods.items()
            if any(wef < unt for wef, unt in periods)
        }

        return self._highlight_periods

    def write(self, plan_filename: str, mode : str = 'w') -> None:
        with open(plan_filename, mode) as f:
            for date, confs in self._uces.items():
                d = date.strftime('%Y-%m-%d %H:%M:%SZ')
                for conf in confs:
                    f.write("%s;%d;%s\n" % (d, len(conf), ' '.join(conf)))


def from_sector_configuration_plan(plan: Dict, wef: datetime.datetime) -> Uces:
    uces = {}
    uces[wef] = [plan['initialConf']]
    if 'pathElement' in plan: # pathElement may be absent if nothing happens
        for t in plan['pathElement']:
            date = datetime.datetime.strptime(t['transition']['at'], Uces.TRANSITION_FORMAT).replace(tzinfo=datetime.timezone.utc)
            if not date in uces:
                uces[date] = []
            uces[date].append(t['conf'])
    return Uces(uces)


def read_uces(filename: str, fieldnames: List[str] | None = None) -> Uces:
    """
    Reads a file containing UCESA.

    Parameters
    ----------
    filename : str
        Path to the input TXT file.
    
    fieldnames : list[str], optional
        Ordered list of the column names. If None, they are inferred from the file header.

    Returns
    -------
    Uces
        An object containing the UCESA.
    """
    uces = {}
    with open(filename, 'r') as csv_in:
        reader = csv.DictReader(csv_in, delimiter=';', fieldnames=fieldnames)
        for row in reader:
            try:
                row_start = datetime.datetime.strptime(row['start'], '%Y-%m-%d %H:%M:%SZ')
            except ValueError:
                row_start = datetime.datetime.strptime(row['start'], '%Y-%m-%d %H:%M:%S')
            row_start = row_start.replace(tzinfo=datetime.timezone.utc)
            if row['conf']:
                row_conf = row['conf'].split(' ')
            else:
                row_conf = []
            if not row_start in uces:
                uces[row_start] = []
            uces[row_start].append(row_conf)
    return Uces(uces)
