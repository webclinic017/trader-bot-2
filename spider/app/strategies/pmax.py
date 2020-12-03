import backtrader as bt
import backtrader.indicators as bti

from app.indicators.pmax import PMax


class PMaxStrategy(bt.Strategy):
    # period = ATR length
    # multiplier = ATR multiplier
    # length = Moving Average length
    # mav = moving average type (ema, sma vs..)
    params = (('period', 10), ('multiplier', 3), ('length', 10))
    lines = ('basic_ub', 'basic_lb', 'final_ub', 'final_lb')

    # sma(hl/2, length) +- multiplier*atr(periyot)
    def __init__(self):
        super().__init__()

        self.order = None
        self.log_pnl = []
        self.lines.signal = PMax(period=self.params.period, multiplier=self.params.multiplier, length=self.params.length)

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
        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the 20 SMA is above the 50 SMA
            if self.signal > 0:
                # self.log(f'BUY CREATE {self.datas[0].close:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            # Otherwise if the 20 SMA is below the 50 SMA
            elif self.signal < 0:
                # self.log(f'SELL CREATE {self.datas[0].close:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                # self.log(f'CLOSE CREATE {self.datas[0].close:2f}')
                self.order = self.close()

    def stop(self):
        with open('logs/pmax_custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')