from os import environ

from binance.client import Client

from app.models import HistoricalData


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
                'open_time': kline[0],
                'open': kline[1],
                'high': kline[2],
                'low': kline[3],
                'close': kline[4],
                'volume': kline[5],
                'close_time': kline[6],
                'number_of_trades': kline[8]
            }

            HistoricalData.create(**data)

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
