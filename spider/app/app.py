import logging

import backtrader as bt
import numpy as np
import pandas as pd
from binance.client import Client

from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.optimizer import StrategyOptimizer
from app.reporter import Reporter
from app.strategies.pmax import PMaxStrategy


class Spider:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        ext_db.connection()
        self.data_collector = DataCollector(self._config)
        self.init_logging()

    def run(self):
        # self.update_history()

        symbol = 'BTCUSDT'
        # limit = 288  # 1 day (5 min)
        # limit = 2016  # 1 week (5 min)
        # limit = 8064  # 1 month (5 min)
        limit = 80640  # 10 month (5 min)
        interval = Client.KLINE_INTERVAL_5MINUTE
        strategy = PMaxStrategy
        params = {
            'period': range(10, 80, 10),
            'multiplier': np.arange(2, 5.1, 0.5),
            'length': range(10, 21, 5),
            'mav': 'T3'
        }
        print("Params: " + str(params))
        data = self.data_collector.get_data_frame(symbol=symbol, interval=interval, limit=limit)
        data.index = pd.to_datetime(data.index, unit='s')

        # son satirdaki bar henuz kapanmadigi icin onu dahil etme
        data.drop(data.tail(1).index, inplace=True)

        optimizer = StrategyOptimizer(data, symbol, interval)
        # result = optimizer.run_single(strategy, params=params, plot=True)
        # result = optimizer.run_opt(strategy, params=params)
        result = optimizer.run_opt(strategy, params=params, wfo=True)

        reporter = Reporter()
        report = reporter.report(result, strategy, log=True, csv=True)
        self.logger.info("Finished.")
        exit()

    def init_cerebro(self, commission, cash, symbol, interval, limit):
        self.cerebro = bt.Cerebro(optreturn=False, stdstats=True)
        self.cerebro.broker.setcommission(commission=commission)
        self.cerebro.broker.set_cash(cash)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="Basic_Stats")
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=70)

        dataframe = self.data_collector.get_data_frame(symbol=symbol, interval=interval, limit=limit)
        dataframe.index = pd.to_datetime(dataframe.index, unit='s')
        data = bt.feeds.PandasData(dataname=dataframe, datetime='open_time')
        self.cerebro.adddata(data)

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)

    def update_history(self):
        self.data_collector.update_history()
