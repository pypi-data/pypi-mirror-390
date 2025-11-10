import numpy as np

from pychanlun.stick import Stick
from pychanlun.stock import Stock


class Fractal(Stock):

    def __init__(self, symbol):
        self.stick = Stick(symbol)
        self.source = self.stick.source
        super().__init__(symbol)

    def _generate_interval(self, interval):
        if self.stick.data.get(interval) is None:
            return None

        stick_rows = list(self.stick.data.get(interval).itertuples())
        rows = []

        for index in range(1, len(stick_rows)):
            prev, cur = stick_rows[index - 1], stick_rows[index]
            nxt = stick_rows[index + 1] if index < len(stick_rows) - 1 else None

            if self._is_top_fractal(prev, cur, nxt):
                cur = cur._replace(low=np.nan)
            elif self._is_bottom_fractal(prev, cur, nxt):
                cur = cur._replace(high=np.nan)
            else:
                cur = cur._replace(high=np.nan, low=np.nan)

            rows.append(cur)

        return self._to_df(rows, ['high', 'low'])

    @staticmethod
    def _is_top_fractal(prev, cur, nxt):
        return cur.high > prev.high and (nxt is None or cur.high > nxt.high)

    @staticmethod
    def _is_bottom_fractal(prev, cur, nxt):
        return cur.low < prev.low and (nxt is None or cur.low < nxt.low)
