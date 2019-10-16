# -*- coding: utf-8 -*-



# noinspection PyMethodMayBeStatic
def get_model_list():
    from .table_database_migration import DatabaseMigration
    from .table_sample import Sample
    # INSERT new table classes here
    from .table_media import Media
    from .table_user_blocked import User_blocked
    from .table_user_message import User_message
    from .table_user_profile import User_profile

    # Add new tables to front of list
    # INSERT new table classes to be inited here
    return [Sample, User_blocked, User_message, Media, User_profile, DatabaseMigration]
