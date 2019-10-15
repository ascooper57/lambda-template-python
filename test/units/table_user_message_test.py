# -*- coding: utf-8 -*-

from api.rdb.model import db_cursor


# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name ='user_message'"
        )
        column_names = set(name for name, _ in cursor.fetchall())

        assert 7 == len(column_names)

        assert 'id' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names

        assert 'from_username_id' in column_names
        assert 'message' in column_names
        assert 'to_username_id' in column_names
        assert 'sns_message_id' in column_names
