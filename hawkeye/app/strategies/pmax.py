import logging
from datetime import datetime

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
              ('mav', 'sma'),
              ('printlog', False))
    logger = logging.getLogger(__name__)

    # sma(hl/2, length) +- multiplier*atr(periyot)
    def __init__(self):
        super().__init__()
        self.order = None
        self.log_pnl = []
        self.lines.pmax = PMax(period=self.p.period, multiplier=self.p.multiplier, length=self.p.length, mav=self.p.mav)
        self.lines.ma = self.lines.pmax.ma
        self.signal = bt.indicators.CrossOver(self.lines.ma, self.lines.pmax)
        self.len_data = len(list(self.datas[0]))
        self.status = "DISCONNECTED"

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.datetime(0)
            self.logger.info('%s, %s' % (dt, txt))

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)

        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")
        else:
            self.log(datetime.now().strftime("%d-%m-%y %H:%M"), "NOT LIVE - %s" % self.status)

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
                    'BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        # Sentinel to None: new orders allowed
        self.order = None

    def next(self):

        if self.status != "LIVE":
            self.log("%s - $%.5f" % (self.status, self.data0.close[0]))
            return

        # Check for open orders
        if self.order:
            return

        filters = {
            "filterType": "LOT_SIZE",
            "minQty": 0.00000100,
            "maxQty": 900.00000000,
            "stepSize": 0.00000100
        }

        market = {
            'amount': {
                'min': 1e-06, 'max': 900.0
            },
            'price': {
                'min': 0.01, 'max': 1000000.0
            },
            'cost': {
                'min': 10.0, 'max': None
            },
            'market': {
                'min': 0.0, 'max': 100.0
            }
        }

        price = (self.data.high[0] + self.data.low[0]) / 2
        size = 0.0005
        self.log('BUY CREATE {:.5f}@{:.5f}   total: {:.5f}'.format(size, price, size * price))

        # Keep track of the created order to avoid a 2nd order
        self.order = self.buy(size=size, price=price)

        return
        if self.position:
            if self.signal < 0:
                size = 0.0005
                self.log('SELL CREATE {:.5f}@{:.5f}   total: {:.5f}'.format(size, price, size * price))
                self.sell()

        else:
            if self.signal > 0:
                # trading rule: min usdt amount is 10$
                size = 0.0005
                self.log('BUY CREATE {:.5f}@{:.5f}   total: {:.5f}'.format(size, price, size * price))

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(size=size, price=price)

    def stop(self):
        with open('logs/pmax_custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
