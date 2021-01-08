import datetime as dt

import backtrader as bt

DEBUG = True


class CustomStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        self.last_operation = "BUY"
        self.status = "DISCONNECTED"

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")
        else:
            print(dt.datetime.now().strftime("%d-%m-%y %H:%M"), "NOT LIVE - %s" % self.status)

    def next(self):
        if self.status != "LIVE":
            self.log("%s - $%.2f" % (self.status, self.data0.close[0]))
            return

        if self.order:
            return

        print('*' * 5, 'NEXT:', bt.num2date(self.data0.datetime[0]), self.data0.close[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected %s' % order.status)
            self.last_operation = None

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def log(self, txt):
        if not DEBUG:
            return

        dt = self.data0.datetime.datetime()
        print('[%s] %s' % (dt.strftime("%d-%m-%y %H:%M"), txt))
