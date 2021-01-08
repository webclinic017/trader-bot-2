import logging
from datetime import datetime

import backtrader as bt


class CloseSMA(bt.Strategy):
    params = (('period', 15),)
    logger = logging.getLogger(__name__)


    def __init__(self):
        self.order = None
        self.log_pnl = []
        sma = bt.indicators.SMA(self.data, period=self.p.period)
        self.crossover = bt.indicators.CrossOver(self.data, sma)

    def log(self, txt, dt=None):
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
        if self.status != "LIVE":
            self.log("%s - $%.2f" % (self.status, self.data0.close[0]))
            return

        if self.order:
            return

        if self.position:
            if self.crossover < 0:
                self.log('SELL CREATE {:.2f}'.format(self.data.close[0]))
                self.sell()

        else:
            if self.crossover > 0:
                self.log('BUY CREATE {:.2f}'.format(self.data.close[0]))
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

    def stop(self):
        with open('logs/custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
