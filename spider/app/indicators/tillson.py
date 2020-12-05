from backtrader.indicators import MovingAverageBase, MovAv


class TillsonMovingAverage(MovingAverageBase):

    alias = ('T3', 'MovingAverageTillsonT3',)

    lines = ('T3',)
    params = (('_movav', MovAv.EMA), ('volume_factor', 0.7))

    def __init__(self):
        ema1 = self.p._movav(self.data, period=self.p.period)
        ema2 = self.p._movav(ema1, period=self.p.period)
        ema3 = self.p._movav(ema2, period=self.p.period)
        ema4 = self.p._movav(ema3, period=self.p.period)
        ema5 = self.p._movav(ema4, period=self.p.period)
        ema6 = self.p._movav(ema5, period=self.p.period)

        # data = (self.data.high + self.data.low + (2 * self.data.close)) / 4

        a = self.p.volume_factor
        a_2 = a * a
        a_3 = a * a * a

        c1 = -1 * a_3
        c2 = 3 * a_2 + 3 * a_3
        c3 = -6 * a_2 - 3 * a - 3 * a_3
        c4 = 1 + 3 * a + a_3 + 3 * a_2
        T3 = c1 * ema6 + c2 * ema5 + c3 * ema4 + c4 * ema3

        self.lines.T3 = T3
        super(TillsonMovingAverage, self).__init__()
