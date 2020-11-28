import pandas as pd
import quantstats
import logging
from binance.client import Client

from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.models import HistoricalData

import backtrader as bt

from app.sizers import LongOnly
from app.strategies import CloseSMA


class Spider:

    def __init__(self, config):
        self._config = config

    def run(self):
        self.init_logging()

        ext_db.connect()
        ext_db.create_tables([HistoricalData])

        data_collector = DataCollector(self.config)
        klines = data_collector.fetch_klines("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, "3 days ago UTC", limit=1000)
        data_collector.save_klines("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, klines)
        dataframe = data_collector.get_data_frame(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1DAY)
        dataframe.index = pd.to_datetime(dataframe.index, unit='s')

        data = bt.feeds.PandasData(dataname=dataframe, datetime='open_time')

        cerebro = bt.Cerebro(optreturn=False, stdstats=True)

        cerebro.broker.setcommission(commission=0.00075)

        cerebro.adddata(data)

        cerebro.addstrategy(CloseSMA)

        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

        cerebro.addsizer(LongOnly)

        # cerebro.addwriter(bt.WriterFile, csv=True, out='logs/log.csv')

        start_portfolio_value = cerebro.broker.getvalue()

        thestrats = cerebro.run()

        end_portfolio_value = cerebro.broker.getvalue()
        thestrat = thestrats[0]
        pnl = end_portfolio_value - start_portfolio_value

        portfolio_stats = thestrat.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        # returns.to_csv('logs/returns.csv')
        quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        # print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
        print(f'Starting Portfolio Value: {start_portfolio_value:2.2f}')
        print(f'Final Portfolio Value: {end_portfolio_value:2.2f}')
        print(f'PnL: {pnl:.2f}')

        cerebro.plot()

    def init_logging(self):

        logformat='%(asctime)s %(levelname)s: %(message)s'

        if self._config.DEBUG:
            logging.basicConfig(format=logformat, level=logging.DEBUG)
        else:
            logging.basicConfig(format=logformat, level=logging.WARN)
