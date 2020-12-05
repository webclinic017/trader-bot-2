import backtrader as bt


class PMaxBand(bt.Indicator):
    # period = ATR length
    # multiplier = ATR multiplier
    # length = Moving Average length
    # mav = moving average type (ema, sma vs..)
    params = (('period', 10), ('multiplier', 3), ('length', 10), ('mav', 'sma'))
    lines = ('str', 'sts', 'fub', 'flb', 'ma')

    def __init__(self):
        self.atr = bt.indicators.AverageTrueRange(period=self.p.period)
        hl2 = (self.data.high + self.data.low) / 2
        if self.p.mav == 'sma':
            self.l.ma = bt.indicators.MovingAverageSimple(hl2, period=self.p.length)
        elif self.p.mav == 'ema':
            self.l.ma = bt.indicators.ExponentialMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'wma':
            self.l.ma = bt.indicators.WeightedMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'ama':
            self.l.ma = bt.indicators.AdaptiveMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'smma':
            self.l.ma = bt.indicators.SmoothedMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'hma':
            self.l.ma = bt.indicators.HullMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'dma':
            self.l.ma = bt.indicators.DicksonMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'tema':
            self.l.ma = bt.indicators.TripleExponentialMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'zlema':
            self.l.ma = bt.indicators.ZeroLagExponentialMovingAverage(hl2, period=self.p.length)
        elif self.p.mav == 'dema':
            self.l.ma = bt.indicators.DoubleExponentialMovingAverage(hl2, period=self.p.length)
        #todo: 1) Tillson eklenmeli.
        #      2) tema, zlema ve dema calismadi.

        # STR
        self.l.str = self.l.ma + (self.atr * self.p.multiplier)

        # STS
        self.l.sts = self.l.ma - (self.atr * self.p.multiplier)

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.fub[0] = self.l.str[0]
            self.l.flb[0] = self.l.sts[0]
        else:
            # =IF(OR(basic_ub<final_ub*,close*>final_ub*),basic_ub,final_ub*)
            if self.l.str[0] < self.l.fub[-1] or self.l.ma[-1] > self.l.fub[-1]:
                self.l.fub[0] = self.l.str[0]
            else:
                self.l.fub[0] = self.l.fub[-1]

            # =IF(OR(basic_lb > final_lb *, close * < final_lb *), sts *, final_lb *)
            if self.l.sts[0] > self.l.flb[-1] or self.l.ma[-1] < self.l.flb[-1]:
                self.l.flb[0] = self.l.sts[0]
            else:
                self.l.flb[0] = self.l.flb[-1]


class PMax(bt.Indicator):
    """
    PMax indicator
    """
    params = (('period', 7), ('multiplier', 3), ('length', 10),('mav', 'sma'))
    lines = ('profix_maximizer', 'ma')
    plotinfo = dict(subplot=False)

    def __init__(self):
        self.pmb = PMaxBand(period=self.p.period, multiplier=self.p.multiplier, length=self.p.length, mav=self.p.mav)
        self.lines.ma = self.pmb.ma

    def next(self):
        if len(self) - 1 == self.p.period:
            self.l.profix_maximizer[0] = self.pmb.fub[0]
            return

        if self.l.profix_maximizer[-1] == self.pmb.fub[-1]:
            if self.pmb.ma[0] <= self.pmb.fub[0]:
                self.l.profix_maximizer[0] = self.pmb.fub[0]
            else:
                self.l.profix_maximizer[0] = self.pmb.flb[0]

        if self.l.profix_maximizer[-1] == self.pmb.flb[-1]:
            if self.pmb.ma[0] >= self.pmb.flb[0]:
                self.l.profix_maximizer[0] = self.pmb.flb[0]
            else:
                self.l.profix_maximizer[0] = self.pmb.fub[0]
