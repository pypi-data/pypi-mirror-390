from pychanlun.stock import Stock
from pychanlun.trend import Trend


class Signal(Stock):

    def __init__(self, segment):
        self.trend = Trend(segment)
        self.source = self.trend.source
        super().__init__(segment.symbol)

    def _generate_interval(self, interval):
        if self.trend.data.get(interval) is None:
            return None

        segment_df = self.trend.pivot.segment.data.get(interval)
        segment_df['signal'] = 0
        trend_rows = list(self.trend.data.get(interval).itertuples())
        rows = []

        for index in range(0, len(trend_rows) - 3, 2):
            cur = trend_rows[index]
            pivot = self._get_range(trend_rows, index + 2)

            if cur.divergence > 0:
                one, two = self._check_signal_one_two(segment_df, pivot)
                if one is not None:
                    rows.append(one)
                if two is not None:
                    rows.append(two)
            three = self._check_signal_three(segment_df, pivot)
            if three is not None:
                rows.append(three)

        return self._to_df(rows, ['high', 'low', 'signal'])

    def _check_signal_one_two(self, segment_df, pivot):
        items = list(segment_df.loc[pivot.start.Index:].itertuples())
        if len(items) < 3:
            return None

        nxt_1 = items[0]
        nxt_3 = items[2]
        if self._is_top(nxt_1) and nxt_3.high < nxt_1.high:
            nxt_1 = nxt_1._replace(signal=-1)
            nxt_3 = nxt_3._replace(signal=-2)
            return nxt_1, nxt_3
        if self._is_bottom(nxt_1) and nxt_3.low > nxt_1.low:
            nxt_1 = nxt_1._replace(signal=1)
            nxt_3 = nxt_3._replace(signal=2)
            return nxt_1, nxt_3
        return None, None

    def _check_signal_three(self, segment_df, pivot):
        items = list(segment_df.loc[pivot.end.Index:].itertuples())
        if len(items) < 3:
            return None

        nxt_2 = items[1]
        nxt_3 = items[2]
        if self._is_top(nxt_2) and nxt_3.low > pivot.high:
            nxt_3 = nxt_3._replace(signal=3)
            return nxt_3
        if self._is_bottom(nxt_2) and nxt_3.low < pivot.low:
            nxt_3 = nxt_3._replace(signal=-3)
            return nxt_3
        return None
