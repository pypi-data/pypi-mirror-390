import pandas as pd
import yfinance as yf

from pychanlun.stock import Stock


class Source(Stock):

    def _generate_interval(self, interval):
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(
                interval=interval,
                period='max',
                actions=False,
                prepost=False
            )
        except Exception as e:
            print(f'download {self.symbol} ({interval}) error：{e}')
            return None

        if df is not None and not df.empty:
            df.columns = df.columns.str.lower()
            df.index.name = 'datetime'

            if ((self.symbol.endswith('.SZ') or self.symbol.endswith('.SS'))
                    and (interval in ['1m', '5m', '30m'])):
                df = self._filter_cn_trading_time(df)

            df = self._calculate_ma(df)
            df = self._calculate_macd(df)
            df = self._calculate_bb(df)
        return df

    @staticmethod
    def _filter_cn_trading_time(df):
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        df = df.tz_convert('Asia/Shanghai')

        time_mask = (((df.index.time >= pd.Timestamp('09:30').time())
                      & (df.index.time <= pd.Timestamp('11:30').time()))
                     | ((df.index.time >= pd.Timestamp('13:00').time())
                        & (df.index.time <= pd.Timestamp('15:00').time())))
        return df[time_mask].copy()

    @staticmethod
    def _calculate_ma(df):
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma30'] = df['close'].rolling(window=30).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        df['ma120'] = df['close'].rolling(window=120).mean()
        df['ma250'] = df['close'].rolling(window=250).mean()
        return df

    @staticmethod
    def _calculate_macd(df):
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_dea'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_dif'] = df['macd'] - df['macd_dea']
        return df

    @staticmethod
    def _calculate_bb(df):
        df['bb'] = df['close'].rolling(window=20).mean()
        rolling_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb'] + (2 * rolling_std)
        df['bb_lower'] = df['bb'] - (2 * rolling_std)
        return df
