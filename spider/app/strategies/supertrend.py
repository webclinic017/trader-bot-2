import backtrader as bt
import backtrader.indicators as bti

from app.indicators.supertrend import SuperTrend


class SuperTrendStrategy(bt.Strategy):
    params = (('period', 10), ('multiplier', 3.0), ('mav', 'EMA'),
              ('length', 10), ('changeAtr', True))

    def __init__(self):
        super().__init__()

        src = (self.datas[0].high + self.datas[0].low) / 2
        self.order = None
        self.log_pnl = []
        # self.lines.mav = bti.MovAv.EMA(src, period=self.params.length)
        self.lines.supertrend = SuperTrend(period=self.params.period, multiplier=self.params.multiplier)
        # self.signal = bti.CrossOver(self.lines.supertrend)

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        # dt = dt or self.datas[0].datetime.datetime(0)
        # print('%s, %s' % (dt, txt))
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Size: {self.order.executed.size:.2f}, Price: {self.order.executed.price:.2f}, Cost: {self.order.executed.value:.2f}')
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Size: {self.order.executed.size:.2f}, Price: {self.order.executed.price:.2f}, Cost: {self.order.executed.value:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):

        pass

    def stop(self):
        with open('logs/custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
