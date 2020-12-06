import json
import datetime

from app.models.optimized_params import OptimizedParams


class BestParameterPicker:
    def __init__(self) -> None:
        super().__init__()
        self._insert_db()

    def _insert_db(self):
        params = {
            'period': 10,
            'multiplier': 3.3,
            'length': 12,
            'mav': 'T3'
        }

        OptimizedParams.create(
            symbol="BTCUSDT",
            interval="15m",
            strategy_name="app.strategies.pmax.PMaxStrategy",
            parameters=params,
            total_open=1,
            total_closed=1,
            total_won=1,
            total_lost=1,
            strike_rate=1,
            win_streak=1,
            lose_streak=1,
            pnl_net=1,
            cagr=1,
            sharpe=1,
            sortino=1,
            volatility=1,
            avg_profit_per_trade=1,
            avg_loss_per_trade=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
