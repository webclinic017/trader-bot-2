import logging
from datetime import datetime
from os import environ
from typing import List

import pandas as pd
from binance.client import Client

from app.db import ext_db
from app.models import HistoricalData


class DataCollector:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        self._api_key = environ.get('API_KEY') or ''
        self._api_secret = environ.get('API_SECRET') or ''
        self.client = Client(self._api_key, self._api_secret)

    def fetch_klines(self, symbol, interval, start_date, end_date=None, limit=500):
        klines = self.client.get_historical_klines(symbol, interval, start_date, end_str=end_date, limit=limit)

        if len(klines) > 0:
            self.logger.debug("Completed download.")
        else:
            self.logger.debug(f"No new data for {symbol} ({interval}) from {start_date}")

        return klines

    def save_klines(self, symbol, interval, klines) -> None:
        if len(klines) == 0:
            return

        self.logger.debug(f"Saving klines of {symbol} ({interval}) into database...")

        def convert(kl) -> HistoricalData:
            data = {
                'symbol': symbol,
                'interval': interval,
                'open_time': kl[0] / 1000,
                'open': kl[1],
                'high': kl[2],
                'low': kl[3],
                'close': kl[4],
                'volume': kl[5],
                'close_time': kl[6] / 1000,
                'number_of_trades': kl[8]
            }
            return HistoricalData(**data)

        with ext_db.atomic():
            objects = map(convert, klines)
            HistoricalData.bulk_create(objects, batch_size=500)

    def get_data_frame(self, symbol=None, interval=None, limit=1000) -> pd.DataFrame:

        query = HistoricalData.select()

        if symbol is not None:
            query = query.where(HistoricalData.symbol == symbol)

        if interval is not None:
            query = query.where(HistoricalData.interval == interval)

        query = query.order_by(HistoricalData.open_time.desc()).limit(limit)
        # query = query.limit(limit)

        historical_data = (query)
        dataframe = pd.DataFrame(list(historical_data.dicts()))
        dataframe = dataframe.sort_values(by=['open_time'], ascending=True, inplace=False)
        dataframe = dataframe.reset_index(drop=True)
        dataframe = dataframe[['open_time',
                               'open',
                               'high',
                               'low',
                               'close',
                               'volume']]
        dataframe.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        dataframe['openinterest'] = 0

        # dataframe['open_time_idx'] = dataframe['open_time']
        # dataframe = dataframe.set_index(['open_time_idx'])
        # dataframe.sort_index(ascending=False, inplace=True)
        return dataframe

    def update_history(self) -> None:
        self.logger.debug("Updating history table...")

        symbol_interval_pairs = self._config.SYMBOL_INTERVAL_PAIRS

        for symbol, interval in symbol_interval_pairs:
            self.logger.debug(f"Updating {symbol} ({interval}) data...")
            close_time = self.get_latest_close_time(symbol, interval)

            if close_time is None:
                start_date = '1 year ago UTC'
                self.logger.info(f"Couldn't find data for {symbol} ({interval}). Will download from {start_date}")
            else:
                start_date = close_time.isoformat()
                self.logger.debug(f"Latest kline was from {start_date}")

            klines = self.fetch_klines(symbol, interval, start_date=start_date, limit=1000)

            self.save_klines(symbol, interval, klines)

    def get_distinct_kline_pairs(self) -> List:
        pairs = (HistoricalData.select(HistoricalData.symbol, HistoricalData.interval)
                 .distinct()
                 .tuples())

        return pairs

    def get_latest_close_time(self, symbol, interval) -> datetime:
        try:
            row = (HistoricalData.select(HistoricalData.close_time)
                   .where(HistoricalData.symbol == symbol, HistoricalData.interval == interval)
                   .order_by(HistoricalData.close_time.desc())).get()

            close_time = row.close_time

        except HistoricalData.DoesNotExist:
            close_time = None

        return close_time
