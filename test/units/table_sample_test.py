# -*- coding: utf-8 -*-

from api.rdb import db_cursor


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def test(empty_database, create_and_delete_user):
    with db_cursor() as cursor:
        cursor.execute(
        "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'sample'"
        )
        column_names = set(name for name, _ in cursor.fetchall())

        assert 9 == len(column_names)

        assert 'id' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names

        assert 'index_key_example' in column_names
        assert 'integer_example' in column_names
        assert 'datetime_example' in column_names
        assert 'text_example' in column_names
        assert 'decimal_example' in column_names
        assert 'boolean_example' in column_names
