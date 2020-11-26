import datetime

import backtrader as bt
import quantstats

from app.sizers import LongOnly
from app.strategies import CloseSMA


def run():
    cerebro = bt.Cerebro(optreturn=False, stdstats=True)
    cerebro.broker.setcommission(commission=0.00075)

    # Set data parameters and add to Cerebro
    data = bt.feeds.YahooFinanceCSVData(
        dataname='data/BTC-USD.csv',
        fromdate=datetime.datetime(2019, 11, 26),
        todate=datetime.datetime(2020, 11, 26),
    )

    cerebro.adddata(data)

    cerebro.addstrategy(CloseSMA)

    # cerebro.addanalyzer(bta.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='PyFolio')

    cerebro.addsizer(LongOnly)

    cerebro.addwriter(bt.WriterFile, csv=True, out='logs/log.csv')

    start_portfolio_value = cerebro.broker.getvalue()

    thestrats = cerebro.run()

    end_portfolio_value = cerebro.broker.getvalue()
    thestrat = thestrats[0]
    pnl = end_portfolio_value - start_portfolio_value

    portfolio_stats = thestrat.analyzers.getbyname('PyFolio')
    returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
    returns.index = returns.index.tz_convert(None)
    returns.to_csv('logs/returns.csv')
    quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

    # print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
    print(f'Starting Portfolio Value: {start_portfolio_value:2.2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:2.2f}')
    print(f'PnL: {pnl:.2f}')

    # cerebro.plot()
