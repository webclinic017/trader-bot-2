import logging

import backtrader as bt
import pandas as pd
import quantstats
from binance.client import Client

from app.binance.data_collector import DataCollector
from app.db import ext_db
from app.models import HistoricalData
from app.strategies import CloseSMA
from app.strategies.ma_crossover import MAcrossover


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
        self.printTradeAnalysis(basic_stats.get_analysis())

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

        # params = {
        #     'pfast': 4,
        #     'pslow': 45,
        #     'debug': True
        # }
        #
        # self.run_strategy(symbol='BTCUSDT',
        #                   interval=Client.KLINE_INTERVAL_1HOUR,
        #                   strategy=MAcrossover,
        #                   params=params,
        #                   limit=2500,
        #                   plot=True)


        limit = 2500
        interval = Client.KLINE_INTERVAL_5MINUTE
        strategy = MAcrossover

        params = {
            'pfast': range(3, 51, 1),
            'pslow': range(30, 205, 5),
        }

        # limit = 2500
        # interval = Client.KLINE_INTERVAL_5MINUTE
        # strategy = CloseSMA
        #
        # params = {
        #     'period': range(3, 35, 1)
        # }

        self.logger.info(f'Running {strategy.__name__}.. Interval: {interval}, datalimit: {limit}')

        self.optimize_strategy(symbol='BTCUSDT',
                               interval=interval,
                               strategy=strategy,
                               params=params,
                               limit=limit,
                               plot=False)


    def init_logging(self):
        logformat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        logging.basicConfig(format=logformat, level=logging.WARNING)

        if self._config.DEBUG:
            logging.getLogger('app').setLevel(logging.DEBUG)

    def update_history(self):
        self.data_collector.update_history()

    def printTradeAnalysis(self, analyzer):
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
