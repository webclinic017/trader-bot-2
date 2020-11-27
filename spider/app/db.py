import os

from sqlalchemy.orm import relationship as _relationship
from sqlalchemy_unchained import *
from sqlalchemy_unchained import _wrap_with_default_query_class
from sqlalchemy.schema import MetaData

from config import config

env = os.getenv('ENV') or 'development'
conf = config[env]

engine = create_engine(conf.POSTGRES_URI)
Session = scoped_session_factory(bind=engine, query_cls=BaseQuery)
SessionManager.set_session_factory(Session)
Model = declarative_base(bind=engine)
relationship = _wrap_with_default_query_class(_relationship, BaseQuery)

Model.metadata.create_all(bind=engine, tables=None, checkfirst=True)
