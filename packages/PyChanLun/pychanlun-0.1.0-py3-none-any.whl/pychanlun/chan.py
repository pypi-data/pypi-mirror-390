import pandas as pd

from pychanlun.segment import Segment
from pychanlun.signal import Signal


class Chan:

    def __init__(self, symbol):
        self.symbol = symbol
        self.segment = Segment(symbol)
        self.stroke_sign = Signal(self.segment.stroke)
        self.segment_sign = Signal(self.segment)

    def get_sticks(self, interval):
        df = self.segment.source.data[interval]
        if df is None:
            return None

        stick_df = self.segment.stroke.fractal.stick.data[interval]
        if stick_df is not None and len(stick_df) > 0:
            stick_df = stick_df.copy().rename(columns={
                'high': 'top',
                'low': 'bottom'
            })
            df = df.join(stick_df[['top', 'bottom']], how='left')
        return df

    def get_fractals(self, interval):
        df = self.segment.stroke.fractal.data[interval]
        if df is None:
            return None

        df = df[df['high'].notna() | df['low'].notna()]
        df = df.copy().rename(columns={
            'high': 'top',
            'low': 'bottom'
        })
        return df[['top', 'bottom']]

    def get_strokes(self, interval):
        df = self.segment.stroke.data[interval]
        if df is None:
            return None

        df['stroke'] = df['high'].fillna(df['low'])
        return df[['stroke']]

    def get_stroke_pivots(self, interval):
        df = self.stroke_sign.trend.data[interval]
        if df is None:
            return None

        return self._get_pivots(df)

    def get_stroke_pivot_trends(self, interval):
        df = self.stroke_sign.trend.data[interval][1:-1]
        if df is None:
            return None

        return self._get_trends(df)

    def get_stroke_pivot_signals(self, interval):
        df = self.stroke_sign.data[interval]
        if df is None:
            return None

        return self._get_signals(df)

    def get_segments(self, interval):
        df = self.segment.data[interval]
        if df is None:
            return None

        df['segment'] = df['high'].fillna(df['low'])
        return df[['segment']]

    def get_segment_pivots(self, interval):
        df = self.segment_sign.trend.data[interval]
        if df is None:
            return None

        return self._get_pivots(df)

    def get_segment_pivot_trends(self, interval):
        df = self.segment_sign.trend.data[interval][1:-1]
        if df is None:
            return None

        return self._get_trends(df)

    def get_segment_pivot_signals(self, interval):
        df = self.segment_sign.data[interval]
        if df is None:
            return None

        return self._get_signals(df)

    @staticmethod
    def _get_pivots(df):
        df = pd.DataFrame({
            'entry': df.index.values[::2],
            'exit': df.index.values[1::2],
            'entry_high': df['high'].values[::2],
            'exit_high': df['high'].values[1::2],
            'entry_low': df['low'].values[::2],
            'exit_low': df['low'].values[1::2],
            'entry_macd': df['macd'].values[::2],
            'exit_macd': df['macd'].values[1::2],
            'trend': df['trend'].values[::2],
            'divergence': df['divergence'].values[::2]
        })
        df['high'] = df['entry_high'].fillna(df['exit_high'])
        df['low'] = df['entry_low'].fillna(df['exit_low'])
        return df[['entry', 'exit', 'high', 'low', 'entry_macd', 'exit_macd', 'trend', 'divergence']]

    @staticmethod
    def _get_trends(df):
        return pd.DataFrame({
            'entry': df.index.values[::2],
            'exit': df.index.values[1::2],
            'entry_price': df['price'].values[::2],
            'exit_price': df['price'].values[1::2]
        })

    @staticmethod
    def _get_signals(df):
        df['price'] = df['high'].fillna(df['low'])
        return df[['price', 'signal']]
