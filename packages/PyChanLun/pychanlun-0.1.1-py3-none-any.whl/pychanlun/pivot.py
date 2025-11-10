from pychanlun.stock import Stock, Range


class Pivot(Stock):

    def __init__(self, segment):
        self.segment = segment
        self.source = self.segment.source
        super().__init__(segment.symbol)

    def _generate_interval(self, interval):
        if self.segment.data.get(interval) is None:
            return None

        segment_rows = list(self.segment.data.get(interval).itertuples())
        rows = []

        index = 0
        while index < len(segment_rows) - 4:
            cur = segment_rows[index]
            range_1 = self._get_range(segment_rows, index + 1)
            range_2 = self._get_range(segment_rows, index + 3)
            pivot_1 = self._get_pivot(range_1, range_2)

            if self._can_start_pivot(pivot_1, cur) and self._has_range_overlap(range_1, range_2):
                step = 0
                while index + step < len(segment_rows) - 7:
                    range_3 = self._get_range(segment_rows, index + step + 5)
                    if self._is_out_of_pivot(pivot_1, range_3):
                        break
                    step += 2

                lst = segment_rows[index + step + 4]
                if self._is_top(range_1.start):
                    range_1.start = range_1.start._replace(high=pivot_1.high)
                    lst = lst._replace(low=pivot_1.low)
                else:
                    range_1.start = range_1.start._replace(low=pivot_1.low)
                    lst = lst._replace(high=pivot_1.high)

                rows.append(range_1.start)
                rows.append(lst)
                index += step + 4
            else:
                index += 1

        index = 0
        while index < len(rows) - 3:
            pivot_1 = self._get_range(rows, index)
            pivot_2 = self._get_range(rows, index + 2)

            if self._has_range_overlap(pivot_1, pivot_2):
                if self._is_top(pivot_1.start):
                    pivot_1.start = pivot_1.start._replace(high=min(pivot_1.start.high, pivot_2.start.high))
                    pivot_2.end = pivot_2.end._replace(low=max(pivot_1.end.low, pivot_2.end.low))
                else:
                    pivot_1.start = pivot_1.start._replace(low=max(pivot_1.start.low, pivot_2.start.low))
                    pivot_2.end = pivot_2.end._replace(high=min(pivot_1.end.high, pivot_2.end.high))

                rows[index] = pivot_1.start
                rows[index + 3] = pivot_2.end
                rows.remove(pivot_1.end)
                rows.remove(pivot_2.start)
            else:
                index += 2

        return self._to_df(rows, ['high', 'low'])

    @staticmethod
    def _get_pivot(range_1, range_2):
        return Range(range_1.start, range_2.end,
                     min(range_1.high, range_2.high),
                     max(range_1.low, range_2.low))

    def _can_start_pivot(self, pvt, cur):
        return (self._is_top(cur) and cur.high > pvt.high) or (self._is_bottom(cur) and cur.low < pvt.low)

    @staticmethod
    def _has_range_overlap(range_1, range_2):
        return range_2.high > range_1.low and range_2.low < range_1.high

    @staticmethod
    def _is_out_of_pivot(range_1, range_2):
        return range_2.high < range_1.low or range_2.low > range_1.high
