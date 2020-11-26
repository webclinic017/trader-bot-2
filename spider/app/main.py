import backtrader as bt
import backtrader.analyzers as bta

from app.sizers import LongOnly
from app.strategies import CloseSMA

cerebro = bt.Cerebro(optreturn=False, stdstats=True)
cerebro.broker.setcommission(commission=0.00075)

# Set data parameters and add to Cerebro
data = bt.feeds.YahooFinanceCSVData(
    dataname='data/BTC-USD.csv',
)

cerebro.adddata(data)

cerebro.addstrategy(CloseSMA)

cerebro.addanalyzer(bta.SharpeRatio, _name='mysharpe')

cerebro.addsizer(LongOnly)

if __name__ == '__main__':
    start_portfolio_value = cerebro.broker.getvalue()

    thestrats = cerebro.run()

    end_portfolio_value = cerebro.broker.getvalue()
    thestrat = thestrats[0]
    pnl = end_portfolio_value - start_portfolio_value

    print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
    print(f'Starting Portfolio Value: {start_portfolio_value:2.2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:2.2f}')
    print(f'PnL: {pnl:.2f}')

    # cerebro.plot()
