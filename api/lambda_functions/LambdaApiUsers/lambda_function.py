# -*- coding: utf-8 -*-

from os import getcwd

import boto3

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

# https://console.aws.amazon.com/cognito/pool/edit/?region=us-east-1&id=us-east-1:e55c591f-df3e-4161-8d54-0fd7e38dfd91

logger = lambda_logger(__name__, getcwd())


#                   ,-----------.
#                   |/users     |
#                   |-----------|
#                   |-----------|
#                   `-----------'
#
#
# ,----------------------.  ,-------------------.
# |GET /users            |  |OPTIONS /users     |
# |----------------------|  |-------------------|
# |.. responses ..       |  |.. responses ..    |
# |200: ListUsersResponse|  |200: Empty         |
# |----------------------|  |-------------------|
# `----------------------'  `-------------------'
#             |                        |
#   ,-----------------.            ,-----.
#   |UsersResponse    |            |Empty|
#   |-----------------|            |-----|
#   |-----------------|            |-----|
#   `-----------------'            `-----'

# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    cognito_idp_client = boto3.client('cognito-idp')

    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        response = cognito_idp_client.list_users(UserPoolId=request_params['cognito_user_pool_id'])
        return response['Users']

    return handle_request(request, context, http_get=http_get)
