import backtrader as bt


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
        # self.sma = bt.indicators.MovingAverageSimple(hl2, period=self.p.length)
        self.l.basic_ub = self.sma + (self.atr * self.p.multiplier)
        self.l.basic_lb = self.sma - (self.atr * self.p.multiplier)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.final_ub[0] = self.l.basic_ub[0]
            self.l.final_lb[0] = self.l.basic_lb[0]
        else:
            # =IF(OR(basic_ub<final_ub*,close*>final_ub*),basic_ub,final_ub*)
            if self.l.basic_ub[0] < self.l.final_ub[-1] or self.data.close[-1] > self.l.final_ub[-1]:
                self.l.final_ub[0] = self.l.basic_ub[0]
            else:
                self.l.final_ub[0] = self.l.final_ub[-1]

            # =IF(OR(baisc_lb > final_lb *, close * < final_lb *), basic_lb *, final_lb *)
            if self.l.basic_lb[0] > self.l.final_lb[-1] or self.data.close[-1] < self.l.final_lb[-1]:
                self.l.final_lb[0] = self.l.basic_lb[0]
            else:
                self.l.final_lb[0] = self.l.final_lb[-1]


class PMax(bt.Indicator):
    """
    Super Trend indicator
    """
    params = (('period', 7), ('multiplier', 3), ('length', 10))
    lines = ('pmax',)
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.pmb = PMaxBand(period=self.p.period, multiplier=self.p.multiplier, length=self.p.length)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.pmax[0] = self.pmb.final_ub[0]
            return

        if self.l.pmax[-1] == self.pmb.final_ub[-1]:
            if self.data.close[0] <= self.pmb.final_ub[0]:
                self.l.pmax[0] = self.pmb.final_ub[0]
            else:
                self.l.pmax[0] = self.pmb.final_lb[0]

        if self.l.pmax[-1] == self.pmb.final_lb[-1]:
            if self.data.close[0] >= self.pmb.final_lb[0]:
                self.l.pmax[0] = self.pmb.final_lb[0]
            else:
                self.l.pmax[0] = self.pmb.final_ub[0]

