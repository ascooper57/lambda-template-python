# -*- coding: utf-8 -*-

from api.rdb.model import db_migrate, DatabaseMigration, db_cursor


# noinspection SpellCheckingInspection,PyUnusedLocal
def test_migration(empty_database):
    # db_migrate will ensure table creation and migration
    db_migrate()

    # check to see if migrations were executed
    migrations = list(DatabaseMigration.select())

    # empty database should have tables and migrations
    with db_cursor() as _c:
        _c.execute(
            """SELECT table_name
                FROM information_schema.tables
               WHERE table_schema='public'
                 AND table_type='BASE TABLE'"""
        )
        table_names = set(_name for _name, in _c.fetchall())

        assert len(table_names) > 0
        assert 'databasemigration' in table_names
