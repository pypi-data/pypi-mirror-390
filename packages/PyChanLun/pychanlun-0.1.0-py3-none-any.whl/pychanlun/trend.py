from pychanlun.pivot import Pivot
from pychanlun.stock import Stock


class Trend(Stock):

    def __init__(self, segment):
        self.pivot = Pivot(segment)
        self.source = self.pivot.source
        super().__init__(segment.symbol)

    def _generate_interval(self, interval):
        if self.pivot.data.get(interval) is None:
            return None

        source_df = self.source.data.get(interval)
        pivot_df = self.pivot.data.get(interval)
        pivot_df['price'] = pivot_df['macd'] = pivot_df['trend'] = pivot_df['divergence'] = 0
        rows = list(pivot_df.itertuples())

        trend_level = 0
        for index in range(0, len(rows) - 3, 2):
            pivot_1 = self._get_range(rows, index)
            pivot_2 = self._get_range(rows, index + 2)

            self._set_macd(pivot_1, pivot_2, source_df)
            trend_level = self._set_trend(pivot_1, pivot_2, trend_level)

            rows[index] = pivot_1.start
            rows[index + 1] = pivot_1.end
            rows[index + 2] = pivot_2.start
            rows[index + 3] = pivot_2.end

        if len(rows) > 0:
            pivot_1 = self._get_range(rows, -2)
            self._set_macd(pivot_1, None, source_df)
            rows[-1] = pivot_1.end

        return self._to_df(rows, ['high', 'low', 'price', 'macd', 'trend', 'divergence'])

    @staticmethod
    def _set_macd(pivot_1, pivot_2, source_df):
        macd_sum = source_df[(pivot_1 is None or source_df.index >= pivot_1.end.Index) &
                             (pivot_2 is None or source_df.index <= pivot_2.start.Index)].macd_dif.sum()
        if pivot_1 is not None:
            pivot_1.end = pivot_1.end._replace(macd=macd_sum)
        if pivot_2 is not None:
            pivot_2.start = pivot_2.start._replace(macd=macd_sum)

    @staticmethod
    def _set_trend(pivot_1, pivot_2, trend):
        if trend == 0:
            pivot_1.start = pivot_1.start._replace(trend=trend)
            pivot_1.end = pivot_1.end._replace(trend=trend + 1)

        if pivot_2.high > pivot_1.high:
            pivot_1.end = pivot_1.end._replace(price=pivot_1.low)
            if trend < 0:
                trend = 0
            trend += 1
            pivot_2.start = pivot_2.start._replace(trend=trend, price=pivot_2.high)
            pivot_2.end = pivot_2.end._replace(trend=trend + 1)
        else:
            pivot_1.end = pivot_1.end._replace(price=pivot_1.high)
            if trend > 0:
                trend = 0
            trend -= 1
            pivot_2.start = pivot_2.start._replace(trend=trend, price=pivot_2.low)
            pivot_2.end = pivot_2.end._replace(trend=trend - 1)

        if 0 < pivot_1.start.trend < pivot_2.start.trend:
            pivot_1.start = pivot_1.start._replace(divergence=(1 if pivot_1.start.macd > pivot_1.end.macd else 0))
        if 0 > pivot_1.start.trend > pivot_2.start.trend:
            pivot_1.start = pivot_1.start._replace(divergence=(1 if pivot_1.start.macd < pivot_1.end.macd else 0))
        pivot_1.end = pivot_1.end._replace(divergence=pivot_1.start.divergence)

        return trend
