from typing import Union

from app import db
from app.models.historical_data import HistoricalData


class HistoricalDataManager(db.ModelManager):
    class Meta:
        model = HistoricalData

    def create(self, commit=False, **kwargs) -> HistoricalData:
        return super().create(commit=commit, **kwargs)

    def find_by_name(self, name) -> Union[HistoricalData, None]:
        return self.get_by(name=name)
