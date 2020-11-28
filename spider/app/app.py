import pandas as pd
import quantstats
import logging
from binance.client import Client
import backtrader as bt

from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.models import HistoricalData

from app.sizers import LongOnly
from app.strategies import CloseSMA


class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return cash / price


class Spider:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

    def run_strategy(self, symbol, interval, strategy, params=None, plot=False):

        if params is None:
            params = {}

        data_collector = DataCollector(self._config)

        dataframe = data_collector.get_data_frame(symbol=symbol, interval=interval)
        dataframe.index = pd.to_datetime(dataframe.index, unit='s')
        data = bt.feeds.PandasData(dataname=dataframe, datetime='open_time')

        cerebro = bt.Cerebro(optreturn=False, stdstats=True)
        cerebro.broker.setcommission(commission=0.00075)
        cerebro.broker.set_cash(100)
        # cerebro.broker.addcommissioninfo(CommInfoFractional())
        # cerebro.broker.set_filler(bt.broker.filler.FixedBarPerc(perc=25))
        cerebro.adddata(data)
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
        # cerebro.addsizer(LongOnly)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=70)

        # self.report_strategy(cerebro, symbol, interval, strategy, params)
        self.report_optimization(cerebro, strategy)

        if plot:
            cerebro.plot()

    def report_strategy(self, cerebro, symbol, interval, strategy, params):
        cerebro.addstrategy(strategy, **params)
        start_portfolio_value = cerebro.broker.getvalue()
        thestrats = cerebro.run()
        end_portfolio_value = cerebro.broker.getvalue()
        thestrat = thestrats[0]
        pnl = end_portfolio_value - start_portfolio_value

        portfolio_stats = thestrat.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        self.logger.info(f'Symbol: {symbol}, Interval: {interval}, Strategy: {strategy.__name__}, Params: {params}')
        self.logger.info(f'Starting Portfolio Value: {start_portfolio_value:2.2f}')
        self.logger.info(f'Final Portfolio Value: {end_portfolio_value:2.2f}')
        self.logger.info(f'PnL: {pnl:.2f}')

    def report_optimization(self, cerebro, strategy):
        params = {
            'period': range(3, 35, 1)
        }
        cerebro.optstrategy(strategy, **params)

        start_portfolio_value = cerebro.broker.getvalue()
        opt_runs = cerebro.run()

        final_results_list = []
        for run in opt_runs:
            for strategy in run:
                value = round(strategy.broker.get_value(), 2)
                PnL = round(value - start_portfolio_value, 2)
                period = strategy.params.period
                final_results_list.append([period, PnL])

        # Sort Results List
        by_PnL = sorted(final_results_list, key=lambda x: x[-1], reverse=True)

        print('Results: Ordered by Profit:')

        for result in by_PnL:
            print('Period: {}, PnL: {}'.format(result[0], result[1]))

    def run(self):
        self.init_logging()

        ext_db.connect()
        ext_db.create_tables([HistoricalData])

        data_collector = DataCollector(self._config)
        # data_collector.update_history()

        params = {
            'period': 15,  # range(3, 35, 1)
        }

        self.run_strategy(symbol='BTCUSDT',
                          interval=Client.KLINE_INTERVAL_1HOUR,
                          strategy=CloseSMA,
                          # params=params,
                          plot=False)

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)
