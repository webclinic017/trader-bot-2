import datetime

from app.models.optimized_params import OptimizedParams


class BestParameterPicker:
    def __init__(self) -> None:
        super().__init__()
        #self._insert_db()

    def pick(self, report_list) -> OptimizedParams:
        sorted_by_pnl = sorted(report_list, key=lambda x: x['pnl_net'])
        maximum_pnl_result = sorted_by_pnl[-1]
        return self._insert_db(maximum_pnl_result)

    def _insert_db(self, data):
        result = OptimizedParams.create(
            symbol="BTCUSDT",
            interval="15m",
            strategy_name="app.strategies.pmax.PMaxStrategy",
            parameters=data['params'],
            total_open=data['total_open'],
            total_closed=data['total_closed'],
            total_won=data['total_won'],
            total_lost=data['total_lost'],
            strike_rate=data['strike_rate'],
            win_streak=data['win_streak'],
            lose_streak=data['lose_streak'],
            pnl_net=data['pnl_net'],
            cagr=data['cagr'],
            sharpe=data['sharpe'],
            sortino=data['sortino'],
            volatility=data['volatility'],
            avg_pnl_per_trade=data['pnl_net'] / data['total_closed'],
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        return result
