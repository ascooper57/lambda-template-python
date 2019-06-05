import contextlib
import datetime
import logging

from peewee import *
# from playhouse.pool import PostgresqlExtDatabase
from playhouse.postgres_ext import *
# noinspection PyUnresolvedReferences
from playhouse.postgres_ext import BinaryJSONField

from ..config import get

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# global db pointer
_db = PostgresqlExtDatabase(
    (get('rdb.pg.database') or None),
    host=(get('rdb.pg.host') or None),
    port=get('rdb.pg.port'),
    user=(get('rdb.pg.username') or None),
    password=(get('rdb.pg.password') or None),
    sslmode=get('rdb.pg.sslmode'),
    autocommit=True,
    register_hstore=True)


@contextlib.contextmanager
def db_cursor():
    # http://docs.peewee-orm.com/en/latest/peewee/changes.html#changes
    conn = _db.connection()
    yield conn.cursor()


def db_close():
    _db.close()


def db_connect():
    _db.connect()


def safe_bootstrap_db():
    from .schema import Schema
    schema = Schema(None)
    all_models = schema.all_models()
    # noinspection PyBroadException,PyUnusedLocal
    try:
        schema.create_models(all_models)
    except Exception as ex:
        pass


def tsvectorfield2string(tsv_string):
    return tsv_string.replace("'", "") if tsv_string else None


class BaseModel(Model):
    class Meta:
        database = _db

    @classmethod
    def atomic(cls):
        return _db.atomic()


class Timestamped(BaseModel):
    """Base class for all peewee models.  This will automatically
       create and maintain updated_at and created_at fields."""

    created_at = DateTimeField(default=datetime.datetime.now(), index=True)
    created_at._sort_key = (2, 1000)
    updated_at = DateTimeField(default=datetime.datetime.now(), index=True)
    updated_at._sort_key = (2, 999)

    def save(self, *args, timestamps=True, **kwargs):
        if timestamps and 'updated_at' not in self._dirty:
            self.updated_at = datetime.datetime.now()
        # noinspection PyCompatibility
        return super().save(*args, **kwargs)

    def prepared(self):
        """Overriding peewee prepared() to properly clear out dirty flags"""
        # noinspection PyCompatibility,PyUnresolvedReferences
        super().prepared()
        self._dirty.clear()


class HavingChildren:
    """Helper for dealing with parent child relationships.
       Assumes a foreign key referencing self named `parent`"""

    # noinspection PyUnresolvedReferences
    @property
    def names(self):
        """Returns all names (including aliases) for a parent/child"""
        names = set(_o.name for _o in self.children if _o.name)
        if self.name:
            names.add(self.name)
        return names

    def add_child(self, child):
        with _db.atomic():
            child.parent = self
            child.save()

    # noinspection PyMethodMayBeStatic
    def remove_child(self, child):
        with _db.atomic():
            child.parent = None
            child.save()

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    def set_children(self, *args):
        with _db.atomic():
            query = self.__class__.update(parent=None).where(self.__class__.parent == self)
            query.execute()
            for child in args:
                child.parent = self
                child.save()
