# -*- coding: utf-8 -*-

from os import getcwd

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                  ,-------.
#                  |/health|
#                  |-------|
#                  |-------|
#                  `-------'
#
#
# ,-------------------.   ,---------------.
# |GET /health        |   |OPTIONS /health|
# |-------------------|   |---------------|
# |.. responses ..    |   |.. responses ..|
# |200: HealthResponse|   |200: Empty     |
# |-------------------|   |---------------|
# `-------------------'   `---------------'
#            |                    |
# ,--------------------.          |
# |HealthResponse      |       ,-----.
# |--------------------|       |Empty|
# |string <b>status</b>|       |-----|
# |--------------------|       |-----|
# `--------------------'       `-----'

# request – AWS Lambda uses this parameter to pass in event data to the handler.
# This parameter is usually of the Python dict type.
# It can also be list, str, int, float, or NoneType type.
# Example: message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])
def handler(request, context):
    # noinspection PyPep8Naming,PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        from api.rdb.model.table_database_migration import DatabaseMigration
        with DatabaseMigration.atomic():
            database_migration = DatabaseMigration.select().limit(1)
            return {"health": 'OK'}

    return handle_request(request, context, http_get=http_get)
