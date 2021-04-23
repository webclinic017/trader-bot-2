from datetime import datetime

from peewee import *

from app.db import BaseExtModel, JSONField


class OptimizedParams(BaseExtModel):
    id = AutoField(primary_key=True)
    symbol = CharField(null=True, max_length=10)
    interval = CharField(null=True, max_length=3)
    strategy_name = CharField(null=True, max_length=32)
    parameters = JSONField(null=True)
    total_open = IntegerField(null=True)
    total_closed = IntegerField(null=False)
    total_won = IntegerField(null=False)
    total_lost = IntegerField(null=False)
    strike_rate = FloatField(null=False)
    win_streak = IntegerField(null=False)
    lose_streak = IntegerField(null=False)
    pnl_net = FloatField(null=False)
    cagr = FloatField(null=False)
    sharpe = FloatField(null=False)
    sortino = FloatField(null=False)
    volatility = FloatField(null=False)
    avg_pnl_per_trade = FloatField(null=False)
    created_at = DateTimeField(null=True, formats='%Y-%m-%d %H:%M:%S.%f', default=datetime.now())

    class Meta:
        table_name = 'optimized_params'
        indexes = (
            (('symbol', 'interval'), True),
        )


OptimizedParams.create_table()

