import logging
from copy import deepcopy

import backtrader as bt
import numpy as np
import pandas as pd
import quantstats
from binance.client import Client
from pandas import DataFrame

from app.analyzers.acctstats import AcctStats
from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.models import HistoricalData
from app.optimizer import StrategyOptimizer
from app.reporter import Reporter
from app.strategies.pmax import PMaxStrategy
from app.timeseriessplit import TimeSeriesSplitImproved


class Spider:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        ext_db.connect()
        ext_db.create_tables([HistoricalData])
        self.data_collector = DataCollector(self._config)
        self.init_logging()

    def run(self):
        # self.update_history()
        symbol = 'BTCUSDT'
        limit = 2997
        interval = Client.KLINE_INTERVAL_15MINUTE
        strategy = PMaxStrategy
        params = {
            'period': range(5, 101, 5),
            'multiplier': np.arange(2, 4.5, 0.5),
            'length': range(10, 16, 2),
            'mav': 'sma'
        }

        data = self.data_collector.get_data_frame(symbol=symbol, interval=interval, limit=limit)
        data.index = pd.to_datetime(data.index, unit='s')

        # son satirdaki bar henuz kapanmadigi icin onu dahil etme
        data.drop(data.tail(1).index, inplace=True)

        optimizer = StrategyOptimizer(data, symbol, interval)
        # result = optimizer.run_single(strategy, params=params, plot=True)
        result = optimizer.run_opt(strategy, params=params)
        # result = optimizer.run_opt(strategy, params=params, wfo=True)

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
