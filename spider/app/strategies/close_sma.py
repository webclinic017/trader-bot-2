import backtrader as bt


class CloseSMA(bt.Strategy):
    params = (('period', 15),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        self.log_pnl.append(f'{dt.isoformat()} {txt}')

    def __init__(self):
        self.log_pnl = []
        sma = bt.indicators.SMA(self.data, period=self.p.period)
        self.crossover = bt.indicators.CrossOver(self.data, sma)

    def next(self):
        if self.crossover > 0:
            self.buy()

        elif self.crossover < 0:
            self.sell()

    def stop(self):
        with open('logs/custom_log.csv', 'w') as e:
            for line in self.log_pnl:
                e.write(line + '\n')
