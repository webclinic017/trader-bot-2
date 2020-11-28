import os


class Config:
    pass
    SYMBOL_INTERVAL_PAIRS = (
        ('BTCUSDT', '5m'),
        ('BTCUSDT', '15m'),
        ('BTCUSDT', '30m'),
        ('BTCUSDT', '1h'),
        ('BTCUSDT', '4h'),
        ('ETHUSDT', '5m'),
        ('ETHUSDT', '15m'),
        ('ETHUSDT', '30m'),
        ('ETHUSDT', '1h'),
        ('ETHUSDT', '4h'),
        ('IOTAUSDT', '5m'),
        ('IOTAUSDT', '15m'),
        ('IOTAUSDT', '30m'),
        ('IOTAUSDT', '1h'),
        ('IOTAUSDT', '4h'),
    )


class DevelopmentConfig(Config):
    DEBUG = True
    POSTGRES_DB = os.getenv('POSTGRES_DB') or ''
    POSTGRES_USER = os.getenv('POSTGRES_USER') or ''
    POSTGRES_PWD = os.getenv('POSTGRES_PASSWORD') or ''
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = 5432
    POSTGRES_URI = f'postgres://{POSTGRES_USER}:{POSTGRES_PWD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'


class ProductionConfig(Config):
    DEBUG = False
    POSTGRES_DB = os.getenv('POSTGRES_DB') or ''
    POSTGRES_USER = os.getenv('POSTGRES_USER') or ''
    POSTGRES_PWD = os.getenv('POSTGRES_PASSWORD') or ''
    POSTGRES_HOST = 'db'  # service name of database in docker-compose.yml
    POSTGRES_PORT = 5432
    POSTGRES_URI = f'postgres://{POSTGRES_USER}:{POSTGRES_PWD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
