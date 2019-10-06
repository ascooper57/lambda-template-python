# -*- coding: utf-8 -*-

from .table_database_migration import DatabaseMigration


# noinspection PyMethodMayBeStatic
def get_model_list():
    from .table_sample import Sample
    # INSERT new table classes here
    from .table_user_profile import User_profile
    from .table_media import Media

    # Add new tables to front of list
    # INSERT new table classes to be inited here
    return [Media, Sample, User_profile, DatabaseMigration]
