from pychanlun.stock import Stock, StockItem
from pychanlun.stroke import Stroke


class Segment(Stock):

    def __init__(self, symbol):
        self.stroke = Stroke(symbol)
        self.source = self.stroke.source
        super().__init__(symbol)

    def _generate_interval(self, interval):
        if self.stroke.data.get(interval) is None:
            return None

        stroke_rows = list(self.stroke.data.get(interval).itertuples())
        rows = []
        temps: list[StockItem] = []

        for index in range(len(stroke_rows)):
            cur = stroke_rows[index]
            temps.append(StockItem(index, cur))

            is_last = index == len(stroke_rows) - 1
            count = len(temps)
            if count == 3:
                temps = self._three_strokes(temps, is_last)
            elif count == 4:
                temps = self._four_strokes(rows, temps, is_last)
            elif count == 5:
                temps = self._five_strokes(rows, temps, is_last)
            elif count >= 6 and count % 2 == 0:
                temps = self._six_strokes(rows, temps, is_last)
            elif count >= 7 and count % 2 != 0:
                temps = self._seven_strokes(rows, temps, is_last)

            if is_last:
                rows.append(cur)

        return self._to_df(rows, ['high', 'low'])

    def _three_strokes(self, temps, is_last):
        cur, nex_2 = temps[0], temps[2]
        return self._process_segment(temps, cur, nex_2, is_last)

    def _four_strokes(self, rows, temps, is_last):
        cur, nxt_1, nxt_3 = temps[0], temps[1], temps[3]
        return self._process_part_segment(rows, temps, cur, nxt_1, nxt_3, is_last)

    def _five_strokes(self, rows, temps, is_last):
        cur, nxt_4 = temps[0], temps[4]
        return self._process_segment(temps, cur, nxt_4, is_last)

    def _six_strokes(self, rows, temps, is_last):
        cur, nxt_3, nxt_5 = temps[0], temps[-3], temps[-1]
        return self._process_part_segment(rows, temps, cur, nxt_3, nxt_5, is_last)

    def _seven_strokes(self, rows, temps, is_last):
        cur, nxt_4, nxt_6 = temps[0], temps[-3], temps[-1]

        if (is_last or self._is_top(cur.item) and nxt_6.item.high >= nxt_4.item.high
                or self._is_bottom(cur.item) and nxt_6.item.low <= nxt_4.item.low):
            rows.append(cur.item)
            if self._is_top(cur.item):
                rows.append(self._lowest_in_middle(temps).item)
            else:
                rows.append(self._highest_in_middle(temps).item)
            return [nxt_6]
        return temps

    def _process_segment(self, temps, cur, nex, is_last):
        if (is_last or self._is_top(cur.item) and nex.item.high >= cur.item.high
                or self._is_bottom(cur.item) and nex.item.low <= cur.item.low):
            return [nex]
        return temps

    def _process_part_segment(self, rows, temps, cur, nxt, lst, is_last):
        if (is_last or self._is_top(cur.item) and lst.item.low <= nxt.item.low
                or self._is_bottom(cur.item) and lst.item.high >= nxt.item.high):
            rows.append(cur.item)
            return [lst]
        return temps

    @staticmethod
    def _lowest_in_middle(temps):
        lowest = None
        for index in range(3, len(temps) - 3):
            low = temps[index]
            if lowest is None or low.item.low < lowest.item.low:
                lowest = low
        return lowest

    @staticmethod
    def _highest_in_middle(temps):
        highest = None
        for index in range(3, len(temps) - 3):
            high = temps[index]
            if highest is None or high.item.high > highest.item.high:
                highest = high
        return highest
