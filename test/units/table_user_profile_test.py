# -*- coding: utf-8 -*-

from api.rdb import db_cursor


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def test(empty_database, create_and_delete_user):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'user_profile'"
        )
        column_names = set(name for name, _ in cursor.fetchall())
        assert 13 == len(column_names)

        assert 'id' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names

        assert 'username' in column_names
        assert 'avatar' in column_names
        assert 'given_name' in column_names
        assert 'family_name' in column_names
        assert 'address_line1' in column_names
        assert 'address_line2' in column_names
        assert 'city' in column_names
        assert 'state_or_province' in column_names
        assert 'postal_code' in column_names
        assert 'country_code' in column_names
