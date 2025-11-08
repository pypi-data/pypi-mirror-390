import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime, timedelta

from atmlab.sinapsis.otmv import OTMV
from atmlab.sinapsis.traffic_counts import SubTotalTrafficCountsType, TrafficCountItem, TrafficCounts


class TrafficCountsPlot(object):

    TRAFFIC_COUNTS_COLORS = {
        SubTotalTrafficCountsType.ATC_ACTIVATED: 'blue',
        SubTotalTrafficCountsType.TACT_ACTIVATED_WITHOUT_FSA: 'cornflowerblue',
        SubTotalTrafficCountsType.IFPL: 'lightblue',
        SubTotalTrafficCountsType.PFD: 'lightblue',
        SubTotalTrafficCountsType.RPL: 'lightblue',
        SubTotalTrafficCountsType.SUSPENDED: '#fff0f5',
        SubTotalTrafficCountsType.TACT_ACTIVATED_WITH_FSA: '#fff0f5',
    }

    def __init__(self, traffic_counts: TrafficCounts):
        self.time = []
        self.all_values = {}
        self.all_bottoms = {}
        self.sustain = []
        self.peak = []
        for subtype in SubTotalTrafficCountsType:
            self.all_values[subtype] = []
            self.all_bottoms[subtype] = []
        for t, item in traffic_counts.items():
            self.time.append(t)
            bottom = 0
            for subtype in SubTotalTrafficCountsType:
                traffic_counts_value = item.value(subtype)
                self.all_values[subtype].append(traffic_counts_value)
                self.all_bottoms[subtype].append(bottom)
                bottom += traffic_counts_value
            self.sustain.append(item.otmv.sustain) # type: ignore
            self.peak.append(item.otmv.peak) # type: ignore
        self.labels = [t.strftime('%H:%M') for t in self.time]
        self.title = traffic_counts.tv
        self.traffic_counts = traffic_counts
        self.set_highlight_periods([(traffic_counts.wef, traffic_counts.unt)])
    
    def set_highlight_periods(self, periods: list[tuple[datetime, datetime]]):
        self.highlight_periods = []
        for start, end in periods:
            self.highlight_periods.append((self.traffic_counts.index_of(start), self.traffic_counts.index_of(end)))
    
    def _alpha_for_index(self, i: int) -> float:
        for start, end in self.highlight_periods:
            if start <= i < end:
                return 1
        return 0.1
        
    def very_slow_plot(self, filename=None):
        bar_width = 1 / 1440  # 1 minute = 1/1440 day
        shifted_times = [t + timedelta(days=bar_width / 2) for t in self.time]
        plt.figure(figsize=(100, 20))
        plt.xticks(self.time, self.labels, rotation=90)
        for subtype, values in self.all_values.items():
            c = TrafficCountsPlot.TRAFFIC_COUNTS_COLORS[subtype]
            colors = [mcolors.to_rgba(c, self._alpha_for_index(i)) for i in range(len(self.time))]
            plt.bar(shifted_times, values, label=subtype.name, width=bar_width, bottom=self.all_bottoms[subtype], color=colors)
        plt.step(self.time, self.sustain, where='post', color='red', linewidth=2, label="Sustain")
        plt.step(self.time, self.peak, where='post', color='orange', linewidth=2, label="Peak")
        # ax = plt.gca()
        # ax.xaxis.set_major_locator(MaxNLocator(nbins=7))
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title(self.title)
        plt.legend()
        plt.tight_layout()
        if filename:
            plt.savefig(filename, dpi=30, bbox_inches='tight')
            plt.clf()
        else:
            plt.show()


if __name__ == '__main__':
    timestamps = [datetime(2025, 1, 1, 0, 0) + timedelta(minutes=i) for i in range(60)]
    items = [TrafficCountItem(ifpl=i, suspended=1, otmv=OTMV(sustain=10, peak=13 + i//10)) for i in range(60)]
    wef = timestamps[0]
    unt = timestamps[-1] + timedelta(minutes=1)
    traffic_counts = TrafficCounts('TEST', wef=wef, unt=unt, step=timedelta(minutes=1), duration=timedelta(minutes=8), items=items)
    plot = TrafficCountsPlot(traffic_counts)
    highlist_periods = [
        (wef + timedelta(minutes=10), wef + timedelta(minutes=20)),
        (wef + timedelta(minutes=30), wef + timedelta(minutes=60))
    ]
    plot.set_highlight_periods(highlist_periods)
    # plot.plot('test.png')
    plot.very_slow_plot()
