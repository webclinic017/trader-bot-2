import os


class Config:
    POSTGRES_DB = os.getenv('POSTGRES_DB') or ''
    POSTGRES_USER = os.getenv('POSTGRES_USER') or ''
    POSTGRES_PWD = os.getenv('POSTGRES_PASSWORD') or ''
    POSTGRES_HOST = ''
    POSTGRES_PORT = 5432
    POSTGRES_URI = f'postgres://{POSTGRES_USER}:{POSTGRES_PWD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'


class DevelopmentConfig(Config):
    DEBUG = True
    POSTGRES_HOST = 'localhost'


class ProductionConfig(Config):
    DEBUG = False
    POSTGRES_HOST = 'db'  # service name of database in docker-compose.yml


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
