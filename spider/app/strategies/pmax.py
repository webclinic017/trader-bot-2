import backtrader as bt

from app.indicators.pmax import PMax


class PMaxStrategy(bt.Strategy):
    # period = ATR length
    # multiplier = ATR multiplier
    # length = Moving Average length
    # mav = moving average type (ema, sma vs..)
    params = (('period', 10),
              ('multiplier', 3),
              ('length', 10),
              ('printlog', False))

    # sma(hl/2, length) +- multiplier*atr(periyot)
    def __init__(self):
        super().__init__()
        self.order = None
        self.log_pnl = []
        self.lines.pmax = PMax(period=self.params.period, multiplier=self.params.multiplier, length=self.params.length)
        self.lines.ma = self.lines.pmax.ma
        self.signal = bt.indicators.CrossOver(self.lines.ma, self.lines.pmax)
        self.len_data = len(list(self.datas[0]))

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        # Sentinel to None: new orders allowed
        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
            return

        if len(self) + 1 >= self.len_data:
            return

        if self.position:
            if self.signal < 0:
                self.log('SELL CREATE {:.2f}'.format(self.data.close[0]))
                self.sell()

        else:
            if self.signal > 0:
                self.log('BUY CREATE {:.2f}'.format(self.data.close[0]))
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

    def stop(self):
        with open('logs/pmax_custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
