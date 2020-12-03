import backtrader as bt

def sma(x, y):
    sum = 0.0
    for i in range(0,y):
        sum = sum + x[i] / y
    print(sum)
    return sum

class PMaxBand(bt.Indicator):
    # period = ATR length
    # multiplier = ATR multiplier
    # length = Moving Average length
    # mav = moving average type (ema, sma vs..)
    params = (('period', 10), ('multiplier', 3), ('length', 10))
    lines = ('basic_ub', 'basic_lb', 'final_ub', 'final_lb')

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.p.period)
        hl2 = (self.data.high + self.data.low) / 2
        self.sma = bt.indicators.SMA(hl2, period=self.p.length)
        self.l.basic_ub = self.sma + (self.atr * self.p.multiplier)
        self.l.basic_lb = self.sma - (self.atr * self.p.multiplier)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.final_ub[0] = self.l.basic_ub[0]
            self.l.final_lb[0] = self.l.basic_lb[0]
        else:
            if self.l.basic_ub[0] < self.l.final_ub[-1] or self.data.close[-1] > self.l.final_ub[-1]:
                self.l.final_ub[0] = self.l.basic_ub[0]
            else:
                self.l.final_ub[0] = self.l.final_ub[-1]

            if self.l.basic_lb[0] > self.l.final_lb[-1] or self.data.close[-1] < self.l.final_lb[-1]:
                self.l.final_lb[0] = self.l.basic_lb[0]
            else:
                self.l.final_lb[0] = self.l.final_lb[-1]

class PMax(bt.Indicator):
    params = (('period', 10), ('multiplier', 3), ('length', 10))
    lines = ('pmax',)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.pb = PMaxBand(period=self.p.period, multiplier=self.p.multiplier)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.pmax[0] = self.stb.final_ub[0]
            return 0

        if self.l.pmax[-1] == self.stb.final_ub[-1]:
            if self.data.close[0] <= self.stb.final_ub[0]:
                self.l.pmax[0] = self.stb.final_ub[0]
            else:
                self.l.pmax[0] = self.stb.final_lb[0]

        if self.l.pmax[-1] == self.stb.final_lb[-1]:
            if self.data.close[0] >= self.stb.final_lb[0]:
                self.l.pmax[0] = self.stb.final_lb[0]
            else:
                self.l.pmax[0] = self.stb.final_ub[0]


if __name__ == '__main__':
    period = 2
    data = [3,5,7]
    sma(data, 2)
    atr = bt.indicators.AverageTrueRange(period)
    print(atr)

    # x = bt.indicators.SMA(data, period=period)
    # print(x)
