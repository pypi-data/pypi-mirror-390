import os, shutil

from datetime import date, datetime
from importlib.resources import files
from typing import Dict, List

from atmlab.sinapsis import resources
from atmlab.sinapsis.traffic_counts import SubTotalTrafficCountsType, TrafficCounts


class HtmlCountsGenerator(object):

    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, results_dir) -> None:
        self.results_dir = results_dir
        self.tvs = []
        self.has_timestamps = False
        
    def add(self, traffic_counts: TrafficCounts, highlight_periods: list[tuple[datetime, datetime]], overloaded_periods: list[tuple[datetime, datetime]]) -> None:
        self.tvs.append(traffic_counts.tv)
        if not self.has_timestamps:
            self._generate_timestamps(traffic_counts)
        gen = TrafficCountsGenerator(self, traffic_counts)
        gen.set_highlight_periods(highlight_periods)
        gen.set_overloaded_periods(overloaded_periods)
        gen.generate()
    
    def _generate_timestamps(self, traffic_counts: TrafficCounts) -> None:
        filename = os.path.join(self.results_dir, 'timestamps.js')
        with open(filename, 'w') as f:
            values = ','.join("'" + d.strftime(HtmlCountsGenerator.TIMESTAMP_FORMAT) + "'" for d, _ in traffic_counts.items())
            f.write("const timestamps=[%s];" % (values))
        self.has_timestamps = True

    def generate(self) -> None:
        self._copy_resource('plot.js')
        self._copy_resource('styles.css')
        self._generate_index()
    
    def _copy_resource(self, filename) -> None:
        dest_path = os.path.join(self.results_dir, filename)
        source = files(resources).joinpath(filename)
        with source.open("rb") as src, open(dest_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
    
    def _generate_index(self) -> None:

        self.tvs.sort()

        head="""\
<head>
  <meta charset="UTF-8" />
  <title>Occupancy curves</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <link rel="stylesheet" href="styles.css">
</head>
"""
        div="""\
  <div id="menu">
  <h3>Select a TV</h3>
  <div id="sectors"></div>
  </div>
  <div id="graph"></div>
"""
        filename = os.path.join(self.results_dir, "index.html")
        with open(filename, "w") as f:
            f.write('<!DOCTYPE html>')
            f.write('<html lang="fr">')
            f.write(head)
            f.write('<body>')
            f.write(div)
            f.write('  <script src="timestamps.js"></script>')
            for tv in self.tvs:
                f.write(f'  <script src="{tv}.js"></script>')
            f.write('  <script src="plot.js"></script>')
            f.write(' <script>')
            f.write(f"  plotCurve(window.curves['{self.tvs[0]}'])")
            f.write('  </script>')
            f.write('</body>')
            f.write('</html>')


class TrafficCountsGenerator(object):

    def __init__(self, html_generator: HtmlCountsGenerator, traffic_counts: TrafficCounts):
        self.html_generator = html_generator
        self.traffic_counts = traffic_counts
        self.all_values : Dict[SubTotalTrafficCountsType, List[int]] = {}
        self.sustain: List[int] = []
        self.peak:List[int] = []
        self.highlight_periods: list[tuple[int, int]] = []
        self.overloaded_periods: list[dict] = []
        self.active_values: Dict[SubTotalTrafficCountsType, List[int]] = {}
        self.inactive_values: Dict[SubTotalTrafficCountsType, List[int]] = {}
        self._fill_all_values()

    def _fill_all_values(self) -> None:
        # Initialize for each sub type
        for subtype in SubTotalTrafficCountsType:
            self.all_values[subtype] = []
        # Read the traffic counts
        for _, item in self.traffic_counts.items():
            # Fill the occupancy values
            for subtype in SubTotalTrafficCountsType:
                traffic_counts_value = item.value(subtype)
                self.all_values[subtype].append(traffic_counts_value)
            # Fill sustain and peak
            self.sustain.append(item.otmv.sustain) # type: ignore
            self.peak.append(item.otmv.peak) # type: ignore
        # Remove sub type where all values are equals to zero
        keys_to_remove = [k for k, v in self.all_values.items() if all(x == 0 for x in v)]
        for k in keys_to_remove:
            del self.all_values[k]

    def set_highlight_periods(self, periods: list[tuple[datetime, datetime]]) -> None:
        self.highlight_periods = []
        for start, end in periods:
            self.highlight_periods.append((self.traffic_counts.index_of(start), self.traffic_counts.index_of(end)))
    
    def set_overloaded_periods(self, periods: list[tuple[datetime, datetime]]) -> None:
        self.overloaded_periods.clear()
        for period in periods:
            overloaded_period = {
                "wef": period[0].strftime(HtmlCountsGenerator.TIMESTAMP_FORMAT),
                "unt": period[1].strftime(HtmlCountsGenerator.TIMESTAMP_FORMAT),
            }
            self.overloaded_periods.append(overloaded_period)
        
    def generate(self) -> None:
        # if not self.highlight_periods:
            # self.set_highlight_periods([(self.traffic_counts.wef, self.traffic_counts.unt)])
        self._split_active_inactive()
        self._write_data()

    def _split_active_inactive(self) -> None:

        def is_active(index) -> bool:
            return any(start <= index < end for start, end in self.highlight_periods)
        
        for subtype, values in self.all_values.items():
            active = []
            inactive = []
            for i, v in enumerate(values):
                if is_active(i):
                    active.append(v)
                    inactive.append(None)
                else:
                    active.append(None)
                    inactive.append(v)
            self.active_values[subtype] = active
            self.inactive_values[subtype] = inactive
        
    def _write_data(self) -> None:
        filename = os.path.join(self.html_generator.results_dir, self.traffic_counts.tv + ".js")
        with open(filename, "w") as f:
            f.write("window.curves = window.curves || {};")
            f.write("window.curves['%s'] = {" % (self.traffic_counts.tv))
            self._write_bars(f, 'bars', self.active_values)
            self._write_bars(f, 'inactive_bars', self.inactive_values)
            f.write("  overloaded_periods: %s," % (str(self.overloaded_periods),))
            f.write("sustain: [%s]," % (",".join(str(v) for v in self.sustain),))
            f.write("peak: [%s]" % (",".join(str(v) for v in self.peak)))
            f.write("};")
        
    def _write_bars(self, f, name, values) -> None:
        f.write("  %s: {" % (name,))
        for subtype, values in values.items():
            value = ",".join("null" if v is None else str(v) for v in values)
            f.write("    %s: [%s]," % (subtype.name, value))
        f.write("  },")


if __name__ == '__main__':

    import json
    from pyatmlab.sinapsis.traffic_counts import TrafficType
    from pyatmlab.sinapsis.uces import read_uces, Uces

    root_dir = "D:/jbedouet/Documents/ATMLab/main/pysinaps2/"
    tv_results_dir = os.path.join(root_dir, "config/plan_687514f604022749d7f74685/2023_11_20/")

    sector_configuration_plan = os.path.join(root_dir, "plans/nest/LFEEFMP", "stat_NOP146_20231120_20231121_Original.txt")
    uces : Uces = read_uces(sector_configuration_plan, fieldnames=['start', 'nb', 'conf'])
    highligh_periods = uces.get_highlight_periods()

    gen = HtmlCountsGenerator(tv_results_dir)

    # filename = os.path.join(tv_results_dir, tv_id + ".json")
    json_files = [os.path.join(tv_results_dir, f) for f in os.listdir(tv_results_dir) if f.endswith('.json')]
    for json_file in json_files:
        with open(json_file, 'r') as f:
            occupancy = json.load(f)
        all_traffic_counts = TrafficCounts.convert2(occupancy)
        traffic_counts = all_traffic_counts[TrafficType.LOAD]
        gen.add(traffic_counts, highligh_periods[traffic_counts.tv], [])
        gen.generate()
