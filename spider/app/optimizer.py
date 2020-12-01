import logging
from typing import Type, List

import backtrader as bt
import pandas as pd

from app.analyzers.acctstats import AcctStats


class StrategyOptimizer:
    logger = logging.getLogger(__name__)
    INIT_CASH = 100
    BINANCE_COMMISSION = 0.00075
    PERCENT_SIZER = 70

    def __init__(self) -> None:
        super().__init__()
        self.cerebro = None
        self.__init_cerebro()

    def __init_cerebro(self):
        self.cerebro = bt.Cerebro(stdstats=False, maxcpus=4)
        self.cerebro.broker.setcash(self.INIT_CASH)
        self.cerebro.broker.setcommission(commission=self.BINANCE_COMMISSION)
        self.cerebro.addanalyzer(AcctStats)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='Basic_Stats')
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=self.PERCENT_SIZER)

    def run_single(self, data: bt.feed.DataBase, strategy: Type[bt.Strategy], params=None) -> bt.MetaStrategy:
        if params is None:
            params = {}

        # todo multiple data feeds
        self.cerebro.adddata(data)
        self.cerebro.addstrategy(strategy, **params)
        result = self.cerebro.run()[0]

        return result

    def run_opt(self, data: pd.DataFrame, strategy: Type[bt.Strategy], params=None, wfo=False) -> List[List[bt.OptReturn]]:
        """
        :param data:
        :param strategy:
        :param params:
        :param wfo: Whether walk forward optimization is active or not.
        :return:
        """

        if params is None:
            params = {}

        if wfo:
            results = None
        else:
            self.cerebro.adddata(data)
            self.cerebro.optstrategy(strategy, **params)
            results = self.cerebro.run()

        return results
