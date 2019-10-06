import datetime
import logging

from peewee import *
from playhouse.migrate import PostgresqlMigrator, migrate

# noinspection PyProtectedMember
from .db import BaseModel, _db
from .model_list import get_model_list
from .table_database_migration import DatabaseMigration

# from playhouse.postgres_ext import TSVectorField

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# global migration check
_has_ensured_migrations = None


def db_migrate():
    return Schema().migrate()


class DatabaseMigrationError(ValueError):
    pass


class NotIndexedError(ValueError):
    pass


# noinspection PyPep8
class Schema(BaseModel):
    migrator = PostgresqlMigrator(_db)

    # https://en.wikipedia.org/wiki/Telephone_numbering_plan
    migrations = (
        # ('001_comment_drop_column', migrator.drop_column('comment', 'comment'),),
        # ('002_comment_alter_column_type', migrator.alter_add_column('comment', 'comment', TSVectorField(null=False)),),
        # ('003_user_add_phone_column',
        #  migrator.add_column('user', 'phone',
        #                      CharField(max_length=14, null=False, default="+15555555")),),
        # ('004_message_add_sns_message_id_column',
        #  migrator.add_column('message', 'sns_message_id',
        #                      TextField(null=True)),),
        # ('005_channel_change_public_column',
        #  migrator.alter_add_column('channel', 'public',
        #                            BooleanField(default=False)),),
        # ('006_comment_add_rating_column',
        #  migrator.add_column('comment', 'rating',
        #                      IntegerField(index=True, default=0)),),
        # # 'str' object has no attribute 'get_db_field'?
        # ('007_comment_add_parent_column',
        #  migrator.add_column('comment', 'parent',
        #                      ForeignKeyField('self', field="parent_id", backref='children', null=True,
        #                                      default=None)),),
        # ('008_guestuser_add_drivers_license_uuid_column',
        #  migrator.add_column('guestuser', 'drivers_license_uuid',
        #                      TextField(null=True, default=None)),),
        # ('009_comment_add_display_column',
        #  migrator.add_column('comment', 'display',
        #                      BooleanField(default=True)),),
        # ('010_user_profile_add_aws_account_id_column',
        #  migrator.add_column('user_profile', 'aws_account_id',
        #                      TextField(null=True, default=None)),),
        # ('011_user_profile_add_aws_access_key_id_column',
        #  migrator.add_column('user_profile', 'aws_access_key_id',
        #                      TextField(null=True, default=None)),),
        # ('012_user_profile_add_aws_secret_access_key_column',
        #  migrator.add_column('user_profile', 'aws_secret_access_key',
        #                      TextField(null=True, default=None)),),
        # ('013_user_profile_add_region_column',
        #  migrator.add_column('user_profile', 'region',
        #                      TextField(null=False, default='us-east-1')),),
    )

    def create_models(self, models=None, ignore_errors=False):
        if models is None:
            models = []
        if not models:
            models = get_model_list()
        self.migrator.database.create_tables(models, safe=ignore_errors)

    def drop_models(self, models=None):
        if models is None:
            models = []
        if not models:
            models = get_model_list()
        self.migrator.database.drop_tables(models, safe=True, cascade=True)

    def ensure_migrations(self):
        global _has_ensured_migrations

        # only do this once
        if not _has_ensured_migrations:
            _has_ensured_migrations = True
            self.validate_migrations()

    def validate_migrations(self):
        # load any completed migrations
        try:
            query = (DatabaseMigration
                     .select()
                     .where(DatabaseMigration.migrated_at.is_null(False)))
            completed_migrations = set([m.name for m in query])
        except ProgrammingError as ex:
            # might not exist yet...
            if '"databasemigration" does not exist' not in str(ex):
                raise
        else:
            # compare with all migrations
            all_migrations = set([name for name, operations in self.migrations])
            missing_migrations = all_migrations - completed_migrations

            if missing_migrations:
                raise DatabaseMigrationError(repr(missing_migrations))

    def migrate(self):
        """Create and ensure proper schema"""
        now = datetime.datetime.utcnow()

        # need to handle migration #0 - create any missing tables
        self.create_models(ignore_errors=True)

        # load any completed migrations
        query = (DatabaseMigration
                 .select()
                 .where(DatabaseMigration.migrated_at.is_null(False)))
        completed_migrations = [m.name for m in query]

        for name, operations in self.migrations:
            if name not in completed_migrations:
                # create a migration with this name
                try:
                    with self.migrator.database.atomic():
                        m = DatabaseMigration.create(name=name)
                except IntegrityError:
                    m = DatabaseMigration.get(DatabaseMigration.name == name)

                with self.migrator.database.atomic():
                    # run the operations
                    try:
                        migrate(operations)
                    except ProgrammingError as ex:
                        if 'already exists' in str(ex):
                            logger.info("Migration %s previous performed, skipped..." % name)
                            pass
                        else:
                            raise
                    except AttributeError as ex:
                        print(str(ex))
                        logger.error(str(ex))

                with DatabaseMigration.atomic():
                    # set the timestamp
                    m.migrated_at = now
                    m.save()
