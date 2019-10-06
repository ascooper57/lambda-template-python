# -*- coding: utf-8 -*-

from api.rdb.model import db_cursor


# noinspection SpellCheckingInspection,PyUnusedLocal
def test(empty_database, create_users):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name ='media'"
        )
        column_names = set(name for name, _ in cursor.fetchall())

        assert 10 == len(column_names)

        assert 'created_at' in column_names
        assert 'updated_at' in column_names

        assert 'media_uuid' in column_names
        assert 'username_id' in column_names
        assert 'tags' in column_names
        assert 'latitude' in column_names
        assert 'longitude' in column_names
        assert 'media_created' in column_names
        assert 'likes' in column_names
        assert 'description' in column_names
