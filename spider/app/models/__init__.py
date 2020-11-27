"""SQLAlchemy Metadata and Session object"""
import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import config

__all__ = ['Session', 'metadata', 'BaseModel']
env = os.getenv('ENV') or 'development'
conf = config[env]
engine = create_engine(conf.POSTGRES_URI)

Session = scoped_session(sessionmaker(bind=engine))
metadata = MetaData()

from sqlalchemy.ext.declarative import declarative_base


class _Base(object):
    _repr_hide = ['time_created', 'time_updated']
    _json_hide = []

    @classmethod
    def get(cls, id):
        return Session.query(cls).get(id)

    @classmethod
    def get_by(cls, **kw):
        return Session.query(cls).filter_by(**kw).first()

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if not r:
            r = cls(**kw)
            Session.add(r)
            Session.commit()
        return r

    @classmethod
    def create(cls, **kw):
        r = cls(**kw)
        Session.add(r)
        Session.commit()
        return r

    def delete(self):
        Session.delete(self)
        Session.commit()

    def _is_loaded(self, key):
        return key in self.__dict__

    def _is_loaded_all(self, path):
        """
        Check if the given path of properties are eager-loaded.
        `path` is similar to sqlalchemy.orm.eagerload_all, checking happens
        by inspecting obj.__data__.
        """
        current = self
        for k in path.split('.'):
            if not current._is_loaded(k):
                return False
            current = getattr(current, k)
            if not current:
                return False
            if isinstance(current, list):
                current = current[0]

        return True

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys() if n not in self._repr_hide)
        return "%s(%s)" % (self.__class__.__name__, values)

    def __json__(self):
        ## Only include local table attributes:
        # return dict((n, getattr(self, n)) for n in self.__table__.c.keys() if n not in self._json_hide)
        ## Include loaded relations recursively:
        return dict((n, v) for n, v in self.__dict__.iteritems() if not n.startswith('_') and n not in self._json_hide)


BaseModel = declarative_base(metadata=metadata, cls=_Base)
BaseModel.metadata.create_all(engine, BaseModel.metadata.tables.values(), checkfirst=True)
