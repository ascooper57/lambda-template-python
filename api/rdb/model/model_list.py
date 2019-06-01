# -*- coding: utf-8 -*-

from .database_migration import DatabaseMigration

# noinspection PyMethodMayBeStatic
def get_model_list():
    from .sample import Sample
    # INSERT new table classes here

    # Add new tables to front of list
    # INSERT new table classes to be inited here
    return [Sample, DatabaseMigration]
