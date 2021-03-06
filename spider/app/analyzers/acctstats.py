import backtrader as bt


class AcctStats(bt.Analyzer):

    def __init__(self):
        self.start_val = self.strategy.broker.get_value()
        self.end_val = None

    def stop(self):
        self.end_val = self.strategy.broker.get_value()

    def get_analysis(self):
        return {
            "start": self.start_val,
            "end": self.end_val,
            "growth": self.end_val - self.start_val,
            "return": self.end_val / self.start_val
        }
