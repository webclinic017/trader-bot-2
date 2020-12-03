import logging
from copy import deepcopy
from typing import Type, List

import backtrader as bt
import pandas as pd
import quantstats

from app.analyzers.acctstats import AcctStats
from app.timeseriessplit import TimeSeriesSplitImproved


class StrategyOptimizer:
    logger = logging.getLogger(__name__)
    INIT_CASH = 100
    BINANCE_COMMISSION = 0.00075
    PERCENT_SIZER = 70

    def __init__(self, data: pd.DataFrame, symbol: str, interval: str) -> None:
        super().__init__()
        self.cerebro = None
        self.symbol = symbol
        self.interval = interval
        self.dataframe = data
        self.btdata = bt.feeds.PandasData(dataname=data, datetime='open_time')
        self.__init_cerebro()

    def __init_cerebro(self):
        self.cerebro = bt.Cerebro(stdstats=False, maxcpus=4)
        self.cerebro.broker.setcash(self.INIT_CASH)
        self.cerebro.broker.setcommission(commission=self.BINANCE_COMMISSION)
        self.cerebro.addanalyzer(AcctStats)
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='Basic_Stats')
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=self.PERCENT_SIZER)

    def run_single(self, strategy: Type[bt.Strategy], params: dict = None) -> bt.MetaStrategy:
        if params is None:
            params = {}
        else:
            for k in params:
                if type(params.get(k)) is range:  # it's kinda gay't
                    self.logger.error("Params shouldn't be range.")
                    exit()

        # todo multiple data feeds
        self.cerebro.adddata(self.btdata)
        self.cerebro.addstrategy(strategy, **params)
        result = self.cerebro.run()[0]

        return result

    def run_opt(self, strategy: Type[bt.Strategy],
                params: dict = None, wfo: bool = False) -> List[List[bt.OptReturn]]:
        """
        :param strategy:
        :param params:
        :param wfo: Whether walk forward optimization is active or not.
        :return:
        """

        if params is None:
            params = {}

        if wfo:
            results = self.walk_forward(strategy, params)

        else:
            self.cerebro.adddata(self.btdata)
            self.cerebro.optstrategy(strategy, **params)
            results = self.cerebro.run()

        return results

    def walk_forward(self, strategy, params):
        tscv = TimeSeriesSplitImproved(10)
        split = tscv.split(self.dataframe, fixed_length=True, train_splits=4, test_splits=1)
        walk_forward_results = list()

        for train, test in split:
            datafeeds = {self.symbol: self.dataframe}
            temp_cerebro = bt.Cerebro(stdstats=False, maxcpus=4)
            temp_cerebro.broker.setcash(self.INIT_CASH)
            temp_cerebro.broker.setcommission(commission=self.BINANCE_COMMISSION)
            temp_cerebro.addanalyzer(AcctStats)
            temp_cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
            temp_cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="Basic_Stats")
            temp_cerebro.addsizer(bt.sizers.PercentSizer, percents=70)

            tester = deepcopy(temp_cerebro)

            temp_cerebro.optstrategy(strategy, **params)

            for s, df in datafeeds.items():
                ddata = bt.feeds.PandasData(dataname=df.iloc[train], name=s, datetime='open_time')
                temp_cerebro.adddata(ddata)

            res = temp_cerebro.run()

            res_params = {r[0].params: self.get_quantstats_results(r[0]) for r in res}
            opt_results = pd.DataFrame(res_params).T.loc[:, "cagr"].sort_values(ascending=False).index[0]
            opt_params = opt_results.__dict__

            tester.addstrategy(strategy, **opt_params)
            for s, df in datafeeds.items():
                ddata = bt.feeds.PandasData(dataname=df.iloc[test], name=s, datetime='open_time')
                tester.adddata(ddata)

            res = tester.run()
            walk_forward_results.append(res)

        return walk_forward_results

    def get_quantstats_results(self, run: bt.MetaStrategy) -> dict:
        quantstats.extend_pandas()
        portfolio_stats = run.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        results = {
            'cagr': quantstats.stats.cagr(returns),
            'sharpe': quantstats.stats.sharpe(returns),
            'sortino': quantstats.stats.sortino(returns),
            'volatility': quantstats.stats.volatility(returns),
            'avg_win': quantstats.stats.avg_win(returns),
            'avg_loss': quantstats.stats.avg_loss(returns),
            'max_drawdown': quantstats.stats.max_drawdown(returns),
        }

        return results