from datetime import datetime
from os import environ

from binance.client import Client

from app.managers.historical_data_manager import HistoricalDataManager
from app.models.historical_data import HistoricalData


class DataCollector:

    def __init__(self, config):
        self._config = config
        self._api_key = environ.get('API_KEY') or ''
        self._api_secret = environ.get('API_SECRET') or ''
        self.client = Client(self._api_key, self._api_secret)

    def fetch_klines(self, symbol, interval, start_date, end_date=None, limit=500):
        klines = self.client.get_historical_klines(symbol, interval, start_date, end_str=end_date, limit=limit)
        print(klines)

    def save(self):
        instance = HistoricalDataManager().create(symbol="BTCUSDT",
                                                  interval=Client.KLINE_INTERVAL_1HOUR,
                                                  open=16501.1,
                                                  high=16750.0,
                                                  low=16465.48,
                                                  close=16674.99,
                                                  volume=3666.26901900,
                                                  close_time=datetime.now(),
                                                  open_time=datetime.now(),
                                                  number_of_trades=63439,
                                                  commit=True)
        a = instance

    def queryDb(self):
        pass
        # query = session.query(HistoricalData). \
        #     filter(HistoricalData.symbol == 'BTCUSDT').statement
        #
        # dataframe = pd.read_sql(query, engine, index_col='id')
        # dataframe = dataframe[['open',
        #                        'high',
        #                        'low',
        #                        'close',
        #                        'volume']]
        # dataframe.columns = ['open', 'high', 'low', 'close', 'volume']
        # dataframe['openinterest'] = 0
        # dataframe.sort_index(inplace=True)
        # dataframe.to_csv('test.csv', index=False)

        # data = bt.feeds.PandasData(dataname=dataframe)


if __name__ == '__main__':
    data_collector = DataCollector()
    data_collector.fetch_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "2020-11-27")
