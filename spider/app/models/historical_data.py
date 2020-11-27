from app import db


class HistoricalData(db.Model):
    class Meta:
        pk = 'id'
        created_at = 'created_at'
        updated_at = 'updated_at'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String, nullable=False)
    interval = db.Column(db.String, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    open_time = db.Column(db.DateTime, nullable=False)
    close_time = db.Column(db.DateTime, nullable=False)
    number_of_trades = db.Column(db.Integer, nullable=False)
