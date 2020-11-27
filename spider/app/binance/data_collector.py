from os import environ

from app.models import HistoricalData
from binance.client import Client

import pandas as pd
import backtrader as bt


class DataCollector:

    def __init__(self, config):
        self._config = config
        self._api_key = environ.get('API_KEY') or ''
        self._api_secret = environ.get('API_SECRET') or ''
        self.client = Client(self._api_key, self._api_secret)

    def fetch_klines(self, symbol, interval, start_date, end_date=None, limit=500):
        klines = self.client.get_historical_klines(symbol, interval, start_date, end_str=end_date, limit=limit)
        return klines

    def save_klines(self, symbol, interval, klines):
        for kline in klines:
            data = {
                'symbol': symbol,
                'interval': interval,
                'open_time': kline[0] / 1000,
                'open': kline[1],
                'high': kline[2],
                'low': kline[3],
                'close': kline[4],
                'volume': kline[5],
                'close_time': kline[6] / 1000,
                'number_of_trades': kline[8]
            }
            try:
                HistoricalData.get_or_create(**data)
            except Exception as e:
                pass

    def get_data_frame(self, symbol=None, interval=None):

        query = HistoricalData.select()

        if symbol is not None:
            query = query.where(HistoricalData.symbol == symbol)

        if interval is not None:
            query = query.where(HistoricalData.interval == interval)

        historical_data = (query)
        dataframe = pd.DataFrame(list(historical_data.dicts()))
        dataframe = dataframe[['open_time',
                               'open',
                               'high',
                               'low',
                               'close',
                               'volume']]
        dataframe.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        dataframe['openinterest'] = 0
        # dataframe.sort_index(inplace=True)
        # dataframe.to_csv('test.csv', index=False)
        return dataframe