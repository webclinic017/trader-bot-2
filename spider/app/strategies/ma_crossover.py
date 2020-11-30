import backtrader as bt


class MAcrossover(bt.Strategy):
    # Moving average parameters
    params = (('pfast', 20),
              ('pslow', 50),
              ('optim', False),
              ('optim_fs', ()),
              ('debug', False))

    def log(self, txt, dt=None):
        if self.params.debug:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')  # Comment this line when running optimization
            self.log_pnl.append(f'{dt.isoformat()} {txt}')

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Order variable will contain ongoing order details/status
        self.order = None

        if self.params.optim:  # Use a tuple during optimization
            self.params.pfast, self.params.pslow = self.params.optim_fs  # fast and slow replaced by tuple's contents

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pfast)
        # self.crossover = bt.indicators.CrossOver(self.slow_sma, self.fast_sma)

        self.log_pnl = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Size: {self.order.executed.size:.8f}, Price: {self.order.executed.price:.5f}, Cost: {self.order.executed.value:.2f}')
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Size: {self.order.executed.size:.8f}, Price: {self.order.executed.price:.5f}, Cost: {self.order.executed.value:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        if self.params.pfast >= self.params.pslow:
            return

        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            # Otherwise if the 20 SMA is below the 50 SMA
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close()

    def stop(self):
        with open('logs/custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
