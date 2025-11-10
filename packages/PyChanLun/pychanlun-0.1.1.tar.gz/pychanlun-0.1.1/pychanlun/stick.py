from pychanlun.source import Source
from pychanlun.stock import Stock


class Stick(Stock):

    def __init__(self, symbol):
        self.source = Source(symbol)
        super().__init__(symbol)

    def _generate_interval(self, interval):
        if self.source.data.get(interval) is None:
            return None

        source_rows = list(self.source.data.get(interval).itertuples())
        rows = []

        prev = cur = None
        index = 0
        while index < len(source_rows) - 1:
            prev, cur = source_rows[index], source_rows[index + 1]
            if self._is_go_up(prev, cur) or self._is_go_down(prev, cur):
                rows.append(prev)
                break
            index += 1

        for i in range(index + 2, len(source_rows)):
            nxt = source_rows[i]
            is_go_up = self._is_go_up(prev, cur)

            if self._can_merge_inside(cur, nxt):
                cur = self._update_stick(cur, nxt, is_go_up)
            elif self._can_merge_outside(cur, nxt):
                cur = self._update_stick(nxt, cur, is_go_up)
            else:
                rows.append(cur)
                prev, cur = cur, nxt

        rows.append(cur)
        return self._to_df(rows, ['high', 'low'])

    @staticmethod
    def _is_go_up(cur, nxt):
        return cur.high <= nxt.high and cur.low <= nxt.low

    @staticmethod
    def _is_go_down(cur, nxt):
        return cur.high >= nxt.high and cur.low >= nxt.low

    @staticmethod
    def _can_merge_inside(cur, nxt):
        return cur.high >= nxt.high and cur.low <= nxt.low

    @staticmethod
    def _can_merge_outside(cur, nxt):
        return cur.high <= nxt.high and cur.low >= nxt.low

    @staticmethod
    def _update_stick(cur, nxt, is_go_up):
        if is_go_up:
            return cur._replace(low=nxt.low)
        else:
            return cur._replace(high=nxt.high)
