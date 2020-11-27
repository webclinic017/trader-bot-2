from peewee import *

from app.db import BaseExtModel


class HistoricalData(BaseExtModel):
    id = AutoField(primary_key=True)
    symbol = CharField(null=False, max_length=10)
    interval = CharField(null=False, max_length=3)
    open = FloatField(null=False)
    high = FloatField(null=False)
    low = FloatField(null=False)
    close = FloatField(null=False)
    volume = FloatField(null=False)
    open_time = TimestampField(null=False, utc=True)
    close_time = TimestampField(null=False, utc=True)
    number_of_trades = IntegerField(null=False)

    class Meta:
        table_name = 'historical_data'
        indexes = (
            (('symbol', 'interval', 'open_time'), True),
        )
