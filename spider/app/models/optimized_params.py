from peewee import *

from app.db import BaseExtModel, JSONField


class OptimizedParams(BaseExtModel):
    id = AutoField(primary_key=True)
    symbol = CharField(null=False, max_length=10)
    interval = CharField(null=False, max_length=3)
    strategy_name = CharField(null=False, max_length=32)
    parameters = JSONField()
    total_open = IntegerField()
    total_closed = IntegerField()
    total_won = IntegerField()
    total_lost = IntegerField()
    strike_rate = FloatField()
    win_streak = IntegerField()
    lose_streak = IntegerField()
    pnl_net = FloatField()
    cagr = FloatField()
    sharpe = FloatField()
    sortino = FloatField()
    volatility = FloatField()
    avg_profit_per_trade = FloatField()
    avg_loss_per_trade = FloatField()
    created_at = DateTimeField()

    class Meta:
        table_name = 'optimized_params'
        indexes = (
            (('symbol', 'interval'), True),
        )
