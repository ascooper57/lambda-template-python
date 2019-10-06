# -*- coding: utf-8 -*-

from os import getcwd

from api.rdb.model.table_user_profile import User_profile
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        user_profile = User_profile.get(username=request_params['username'])
        return user_profile.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        with User_profile.atomic():
            # user_profile = User_profile.create(**request_body)
            user_profile, created = User_profile.get_or_create(username=request_body['username'], defaults=request_body)
            if created:
                logger.info("User profile created: %s" % request_body['username'])
            # noinspection PyProtectedMember
            return user_profile.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_post")
        # noinspection PyShadowingBuiltins, PyUnresolvedReferences
        user_profile = User_profile.get(User_profile.username == request_body["username"])
        if "username" in request_body:
            user_profile.username = request_body["username"]
        if "avatar" in request_body:
            user_profile.media_uuid = request_body["avatar"]
        if "given_name" in request_body:
            user_profile.given_name = request_body["given_name"]
        if "family_name" in request_body:
            user_profile.family_name = request_body["family_name"]
        # save updated fields
        with user_profile.atomic():
            user_profile.save()
        return user_profile.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_delete")
        with User_profile.atomic():
            # noinspection PyUnresolvedReferences
            User_profile.delete().where(User_profile.id == request_params["id"]).execute()
            return {}

    # noinspection PyPep8
    return handle_request(request, context, http_get=http_get, http_put=http_put, http_post=http_post,
                          http_delete=http_delete)
