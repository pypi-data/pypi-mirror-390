from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


class Stock(ABC):

    def __init__(self, symbol, auto_generate=True):
        self.symbol = symbol
        self.intervals = ['1m', '5m', '30m', '1d', '1wk', '1mo']

        self.name = self.__class__.__name__.lower()
        self.data: Dict[str, pd.DataFrame | None] = {}

        if auto_generate:
            self.generate()

    def generate(self):
        for interval in self.intervals:
            self.data[interval] = self._generate_interval(interval)

    @abstractmethod
    def _generate_interval(self, interval):
        pass

    @staticmethod
    def _to_df(rows, columns=None):
        if len(rows) == 0:
            return None
        df = pd.DataFrame(rows).set_index('Index')
        df.index.name = 'datetime'
        return df if columns is None else df[columns]

    @staticmethod
    def _is_top(item):
        return np.isnan(item.low) and not np.isnan(item.high)

    @staticmethod
    def _is_bottom(item):
        return np.isnan(item.high) and not np.isnan(item.low)

    def _get_range(self, rows, index):
        start, end = rows[index], rows[index + 1]
        high = start.high if self._is_top(start) else end.high
        low = start.low if self._is_bottom(start) else end.low
        return Range(start, end, high, low)


@dataclass
class StockItem:
    index: int
    item: Stock


@dataclass
class Range:
    start: Stock
    end: Stock
    high: float
    low: float
