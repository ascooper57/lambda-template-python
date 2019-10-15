# -*- coding: utf-8 -*-


from os import getcwd

import boto3
from peewee import DoesNotExist

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request
from api.rdb.model.table_user_profile import User_profile

logger = lambda_logger(__name__, getcwd())


#                                                              ,--------.
#                                                              |/blocked|
#                                                              |--------|
#                                                              |--------|
#                                                              `--------'
#
#
# ,-----------------------------.                                     ,-------------------------.
# |GET /blocked                 |  ,------------------------------.   |DELETE /blocked          |
# |-----------------------------|  |PUT /blocked                  |   |-------------------------|   ,----------------.
# |.. query ..                  |  |------------------------------|   |.. query ..              |   |OPTIONS /blocked|
# |string <b>recipient_email</b>|  |.. body ..                    |   |string <b>id</b>         |   |----------------|
# |string <b>blocked_email</b>  |  |BlockedForm <b>BlockedForm</b>|   |.. responses ..          |   |.. responses .. |
# |.. responses ..              |  |.. responses ..               |   |200: Empty               |   |200: Empty      |
# |200: BlockedResponse         |  |200: BlockedResponse          |   |404: <i>not specified</i>|   |----------------|
# |404: <i>not specified</i>    |  |------------------------------|   |-------------------------|   `----------------'
# |-----------------------------|  `------------------------------'   `-------------------------'
# `-----------------------------'                  |
#                                                  |
#      ,----------------------.                    |
#      |BlockedResponse       |     ,-----------------------------.
#      |----------------------|     |BlockedForm                  |                          ,-----.
#      |boolean <b>blocked</b>|     |-----------------------------|                          |Empty|
#      |integer id            |     |string <b>recipient_email</b>|                          |-----|
#      |string updated_at     |     |string <b>blocked_email</b>  |                          |-----|
#      |string created_at     |     |-----------------------------|                          `-----'
#      |----------------------|     `-----------------------------'
#      `----------------------'

# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    global logger
    from api.rdb.model.table_user_blocked import User_blocked

    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        cognito_idp_client = boto3.client('cognito-idp')
        recipient_user_profile = User_profile.get(User_profile.username == request_params['recipient_username'])
        blocked_user_profile = User_profile.get(User_profile.username == request_params['blocked_username'])

        try:
            # noinspection PyUnresolvedReferences
            result = User_blocked.get(User_blocked.recipient_username == recipient_user_profile.id,
                                      User_blocked.blocked_username == blocked_user_profile.id)
            # noinspection PyProtectedMember
            return {"blocked": True, "id": result.__data__['id']}
        except DoesNotExist as ex:
            return {"blocked": False}

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        cognito_idp_client = boto3.client('cognito-idp')
        recipient_user_profile = User_profile.get(User_profile.username == request_body['recipient_username'])
        blocked_user_profile = User_profile.get(User_profile.username == request_body['blocked_username'])
        defaults = request_body
        with User_blocked.atomic():
            defaults['recipient_username'] = recipient_user_profile
            defaults['blocked_username'] = blocked_user_profile
            # noinspection PyUnresolvedReferences
            user_blocked, created = User_blocked.get_or_create(recipient_username=recipient_user_profile.id,
                                                               blocked_username=blocked_user_profile.id,
                                                               defaults=defaults)
        if created:
            logger.info("Contact: %s blocked: %s" % (recipient_user_profile, blocked_user_profile))
        data = user_blocked.__data__
        # noinspection PyProtectedMember
        return user_blocked.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_delete")
        # noinspection PyUnresolvedReferences
        with User_blocked.atomic():
            # noinspection PyUnresolvedReferences
            User_blocked.delete().where(User_blocked.id == request_params["id"]).execute()
        return {}

    return handle_request(request, context, http_get=http_get, http_put=http_put, http_delete=http_delete)
