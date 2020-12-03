import logging
import random
from copy import deepcopy

import backtrader as bt
import pandas as pd
import quantstats
from binance.client import Client
from pandas import DataFrame

from app.indicators.pmax import PMax
from app.strategies.supertrend import SuperTrendStrategy
from app.timeseriessplit import TimeSeriesSplitImproved
from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.models import HistoricalData
from app.strategies import CloseSMA
from app.strategies.ma_crossover import MAcrossover
from app.strategies.smac import AcctStats, PropSizer, SMAC


class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return cash / price


class Spider:
    logger = logging.getLogger(__name__)

    def __init__(self, config):
        self._config = config

        ext_db.connect()
        ext_db.create_tables([HistoricalData])
        self.data_collector = DataCollector(self._config)
        self.init_logging()

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

    def run_strategy(self, symbol, interval, strategy, params=None, limit=2500, plot=False):
        if params is None:
            params = {}

        self.init_cerebro(commission=0.00075, cash=100, symbol=symbol, interval=interval, limit=limit)
        self.report_strategy(symbol, interval, strategy, params)

        if plot:
            self.cerebro.plot()

    def optimize_strategy(self, symbol, interval, strategy, params=None, limit=2500, plot=False):
        if params is None:
            params = {}

        self.init_cerebro(commission=0.00075, cash=100, symbol=symbol, interval=interval, limit=limit)
        self.report_optimization(strategy, params)

        if plot:
            self.cerebro.plot()

    def report_strategy(self, symbol, interval, strategy, params):
        self.cerebro.addstrategy(strategy, **params)
        start_portfolio_value = self.cerebro.broker.getvalue()
        thestrats = self.cerebro.run()
        end_portfolio_value = self.cerebro.broker.getvalue()
        thestrat = thestrats[0]
        pnl = end_portfolio_value - start_portfolio_value

        quantstats.extend_pandas()
        portfolio_stats = thestrat.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        self.logger.info('CAGR: {:.3f}'.format(quantstats.stats.cagr(returns)))
        self.logger.info('Sharpe: {:.3f}'.format(quantstats.stats.sharpe(returns)))
        self.logger.info('Sortino: {:.3f}'.format(quantstats.stats.sortino(returns)))
        self.logger.info('Volatility: {:.3f}'.format(quantstats.stats.volatility(returns)))
        self.logger.info('Avg Win: {:.5f}'.format(quantstats.stats.avg_win(returns)))
        self.logger.info('Avg Loss: {:.5f}'.format(quantstats.stats.avg_loss(returns)))
        self.logger.info('Max Drawdown: {:.5f}'.format(quantstats.stats.max_drawdown(returns)))

        basic_stats = thestrat.analyzers.getbyname('Basic_Stats')
        self.print_trade_analysis(basic_stats.get_analysis())

        self.logger.info(f'Symbol: {symbol}, Interval: {interval}, Strategy: {strategy.__name__}, Params: {params}')
        self.logger.info(f'Starting Portfolio Value: {start_portfolio_value:2.2f}')
        self.logger.info(f'Final Portfolio Value: {end_portfolio_value:2.2f}')
        self.logger.info(f'PnL: {pnl:.2f}')

    def report_optimization(self, strategy, params):
        self.cerebro.optstrategy(strategy, **params)
        start_portfolio_value = self.cerebro.broker.getvalue()
        opt_runs = self.cerebro.run()

        final_results_list = []
        for run in opt_runs:
            for strat in run:
                value = round(strat.broker.get_value(), 2)
                PnL = round(value - start_portfolio_value, 2)
                pars = vars(strat.params).items()
                final_results_list.append([pars, PnL])

        # Sort Results List
        by_PnL = sorted(final_results_list, key=lambda x: x[-1], reverse=True)

        print('Results: Ordered by Profit:')

        for result in by_PnL:
            print('Period: {}, PnL: {}'.format(result[0], result[1]))

    def run(self):

        # self.update_history()
        symbol = 'BTCUSDT'
        limit = 3000
        interval = Client.KLINE_INTERVAL_1HOUR
        strategy = SuperTrendStrategy
        # params = {
        #     'pfast': 41,
        #     'pslow': 177,
        #     'debug': False
        # }

        params = {
            'period': 7,
            'multiplier': 3,
        }
        self.logger.info(f'Running {strategy.__name__}.. Interval: {interval}, datalimit: {limit}')

        # params = {
        #     'pfast': range(20, 30, 1),
        #     'pslow': range(50, 60, 5),
        # }

        # self.walk_forward(commission=0.00075, cash=100, symbol=symbol, interval=interval, strategy=strategy, params=params, limit=limit)
        #
        self.run_strategy(symbol=symbol,
                          interval=interval,
                          strategy=strategy,
                          params=params,
                          limit=limit,
                          plot=True)

        # limit = 2500
        # interval = Client.KLINE_INTERVAL_5MINUTE
        # strategy = MAcrossover
        #
        # params = {
        #     'pfast': range(48, 51, 1),
        #     'pslow': range(180, 205, 5),
        # }

        #
        # params = {
        #     'period': range(3, 35, 1)
        # }

        # self.logger.info(f'Optimizing {strategy.__name__}.. Interval: {interval}, datalimit: {limit}')

        # self.optimize_strategy(symbol='BTCUSDT',
        #                        interval=interval,
        #                        strategy=strategy,
        #                        params=params,
        #                        limit=limit,
        #                        plot=False)

    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)

    def update_history(self):
        self.data_collector.update_history()

    def print_trade_analysis(self, analyzer):
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total, 2)
        strike_rate = (total_won / total_closed) * 100

        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
        r1 = [total_open, total_closed, total_won, total_lost]
        r2 = [strike_rate, win_streak, lose_streak, pnl_net]

        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)

        print_list = [h1, r1, h2, r2]
        row_format = "{:<15}" * (header_length + 1)
        self.logger.info("Trade Analysis Results:")

        for row in print_list:
            self.logger.info(row_format.format('', *row))

    def get_quantstats_results(self, run: bt.MetaStrategy) -> dict:
        quantstats.extend_pandas()
        portfolio_stats = run.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        results = {'cagr': quantstats.stats.cagr(returns),
                   'sharpe': quantstats.stats.sharpe(returns),
                    'sortino': quantstats.stats.sortino(returns),
                    'volatility': quantstats.stats.volatility(returns),
                    'avg_win': quantstats.stats.avg_win(returns),
                    'avg_loss': quantstats.stats.avg_loss(returns),
                    'max_drawdown': quantstats.stats.max_drawdown(returns),
        }

        return results

    def print_quantstats_results(self, results):
        self.logger.info('CAGR: {:.3f}'.format(results['cagr']))
        self.logger.info('Sharpe: {:.3f}'.format(results['sharpe']))
        self.logger.info('Sortino: {:.3f}'.format(results['sortino']))
        self.logger.info('Volatility: {:.3f}'.format(results['volatility']))
        self.logger.info('Avg Win: {:.5f}'.format(results['avg_win']))
        self.logger.info('Avg Loss: {:.5f}'.format(results['avg_loss']))
        self.logger.info('Max Drawdown: {:.5f}'.format(results['max_drawdown']))

    def walk_forward(self, commission, cash, symbol, interval, strategy, params, limit):

        dataframe = self.data_collector.get_data_frame(symbol=symbol, interval=interval, limit=limit)
        tscv = TimeSeriesSplitImproved(10)
        split = tscv.split(dataframe, fixed_length=True, train_splits=4, test_splits=1)
        walk_forward_results = list()

        for train, test in split:
            datafeeds = {"BTCUSDT": dataframe}
            #TODO burda stdstats niye false initte niye true? bak
            self.cerebro = bt.Cerebro(stdstats=False, maxcpus=4)
            self.cerebro.broker.setcash(cash)
            self.cerebro.broker.setcommission(commission=commission)
            self.cerebro.addanalyzer(AcctStats)
            self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')
            self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="Basic_Stats")
            self.cerebro.addsizer(bt.sizers.PercentSizer, percents=70)
            tester = deepcopy(self.cerebro)

            self.cerebro.optstrategy(strategy, **params)

            for s, df in datafeeds.items():
                data = bt.feeds.PandasData(dataname=df.iloc[train], name=s, datetime='open_time')
                self.cerebro.adddata(data)

            res = self.cerebro.run()

            # Get optimal combination
            # res_params = {r[0].params: r[0].analyzers.acctstats.get_analysis() for r in res}
            res_params = {r[0].params: self.get_quantstats_results(r[0]) for r in res}
            opt_results = DataFrame(res_params).T.loc[:, "cagr"].sort_values(ascending=False).index[0]
            opt_params= opt_results.__dict__
            #TODO: _
            # 1) getpairs guncel parametreleri donmuyor. FIXED
            # 2) Yukarıdaki optimal kombinasyon hesabı maximum return'e gore yapiliyor, daha iyi bir cozum ile degistirilecek (riski de iceren bir metrik) FIXED
            # Not: (Eger data limit kucuk olursa parametreleri dusurmek gerekiyor MACROSSOVER icin yoksa islem yapmiyor.)

            # TESTING
            tester.addstrategy(strategy, **opt_params)
            for s, df in datafeeds.items():
                data = bt.feeds.PandasData(dataname=df.iloc[test], name=s, datetime='open_time')
                tester.adddata(data)

            res = tester.run()[0]
            res_dict = res.analyzers.acctstats.get_analysis()
            res_dict["params"] = opt_params
            walk_forward_results.append(res_dict)

            print(res_dict)
            basic_stats = res.analyzers.getbyname('Basic_Stats')
            self.print_trade_analysis(basic_stats.get_analysis())
            quantstats_result = self.get_quantstats_results(res)
            self.print_quantstats_results(quantstats_result)

        wfdf = DataFrame(walk_forward_results)
        print(wfdf)
