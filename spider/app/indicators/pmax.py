import backtrader as bt

# from app.indicators.tillson import TillsonMovingAverage
from app.indicators.tillson import TillsonMovingAverage


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
        self.p.mav = str(self.p.mav).lower()

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
        elif self.p.mav == 'T3':
            self.l.ma = TillsonMovingAverage(self.data, period=self.p.length, volume_factor=0.7)

        # STR
        self.l.str = self.l.ma + (self.atr * self.p.multiplier)

        # STS
        self.l.sts = self.l.ma - (self.atr * self.p.multiplier)

        self.odd_bar_count = 0

    def prenext(self):
        self.odd_bar_count = len(self)

    def next(self):
        if len(self) == self.odd_bar_count + 1:
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
    params = (('period', 7), ('multiplier', 3), ('length', 10), ('mav', 'sma'))
    lines = ('profix_maximizer', 'ma')
    plotinfo = dict(subplot=True)

    def __init__(self):
        self.pmb = PMaxBand(period=self.p.period, multiplier=self.p.multiplier, length=self.p.length, mav=self.p.mav)
        self.lines.ma = self.pmb.ma
        self.odd_bar_count = 0

    def prenext(self):
        self.odd_bar_count = len(self)

    def next(self):
        if len(self) == self.odd_bar_count + 1:
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
