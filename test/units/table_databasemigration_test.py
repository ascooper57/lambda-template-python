# -*- coding: utf-8 -*-

from api.rdb import db_cursor


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def test(empty_database):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'databasemigration'"
        )
        column_names = set(name for name, _ in cursor.fetchall())

        assert 3 == len(column_names)

        assert 'id' in column_names
        assert 'name' in column_names
        assert 'migrated_at' in column_names
