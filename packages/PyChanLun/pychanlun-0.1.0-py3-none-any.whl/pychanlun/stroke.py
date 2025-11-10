from pychanlun.fractal import Fractal
from pychanlun.stock import Stock, StockItem


class Stroke(Stock):

    def __init__(self, symbol):
        self.fractal = Fractal(symbol)
        self.source = self.fractal.source
        super().__init__(symbol)

    def _generate_interval(self, interval):
        if self.fractal.data.get(interval) is None:
            return None

        fractal_rows = list(self.fractal.data.get(interval).itertuples())
        rows = []
        temps: list[StockItem] = []

        for index in range(len(fractal_rows)):
            cur = fractal_rows[index]

            if self._is_fractal(cur):
                temps.append(StockItem(index, cur))

                is_last = index == len(fractal_rows) - 1
                count = len(temps)
                if count == 2:
                    temps = self._two_fractals(rows, temps, is_last)
                elif count == 3:
                    temps = self._three_fractals(temps, is_last)
                elif count == 4:
                    temps = self._four_fractals(rows, temps, is_last)
                elif count == 5:
                    temps = self._five_fractals(rows, temps, is_last)
                elif count == 6:
                    temps = self._six_fractals(rows, temps)

                if is_last:
                    rows.append(cur)

        return self._to_df(rows, ['high', 'low'])

    def _is_fractal(self, cur):
        return self._is_top(cur) or self._is_bottom(cur)

    @staticmethod
    def _two_fractals(rows, temps, is_last):
        cur, nxt_1 = temps[0], temps[1]
        return Stroke._process_stroke(rows, temps, cur, nxt_1, is_last)

    def _three_fractals(self, temps, is_last):
        cur, nxt_2 = temps[0], temps[2]
        return self._process_part_stroke(temps, cur, nxt_2, is_last)

    @staticmethod
    def _four_fractals(rows, temps, is_last):
        cur, nxt_3 = temps[0], temps[3]
        return Stroke._process_stroke(rows, temps, cur, nxt_3, is_last)

    def _five_fractals(self, rows, temps, is_last):
        cur, nxt_4 = temps[0], temps[4]
        return self._process_part_stroke(temps, cur, nxt_4, is_last)

    @staticmethod
    def _six_fractals(rows, temps):
        cur, nxt_5 = temps[0], temps[5]
        rows.append(cur.item)
        return [nxt_5]

    @staticmethod
    def _process_stroke(rows, temps, cur, nxt, is_last):
        if is_last or nxt.index - cur.index >= 4:
            rows.append(cur.item)
            return [nxt]
        return temps

    def _process_part_stroke(self, temps, cur, nxt, is_last):
        if (is_last or (self._is_top(cur.item) and nxt.item.high >= cur.item.high)
                or (self._is_bottom(cur.item) and nxt.item.low <= cur.item.low)):
            return [nxt]
        return temps
