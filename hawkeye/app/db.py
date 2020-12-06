import os

from playhouse.postgres_ext import *

from config import config

env = os.getenv('ENV') or 'development'
conf = config[env]

ext_db = PostgresqlExtDatabase(conf.POSTGRES_DB,
                               user=conf.POSTGRES_USER,
                               password=conf.POSTGRES_PWD,
                               host=conf.POSTGRES_HOST)


class BaseExtModel(Model):
    class Meta:
        database = ext_db
