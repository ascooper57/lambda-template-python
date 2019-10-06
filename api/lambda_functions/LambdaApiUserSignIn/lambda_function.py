# -*- coding: utf-8 -*-

from os import getcwd

import boto3

from api.rdb.config import get
from api.rdb.utils.cognito import get_cognito_app_client_id
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                                                ,------.
#                                                |/login|
#                                                |------|
#                                                |------|
#                                                `------'
#
#
#                          ,--------------------------.
#                          |POST /login               |   ,---------------.
#                          |--------------------------|   |OPTIONS /login |
#                          |.. body ..                |   |---------------|
#                          |LoginForm <b>LoginForm</b>|   |.. responses ..|
#                          |.. responses ..           |   |200: Empty     |
#                          |200: LoginResponse        |   |---------------|
#                          |--------------------------|   `---------------'
#                          `--------------------------'           |
#                                                                 |
# ,--------------------------.                                    |
# |LoginResponse             |                                    |
# |--------------------------|  ,----------------------.          |
# |string <b>user</b>        |  |LoginForm             |       ,-----.
# |string <b>access_token</b>|  |----------------------|       |Empty|
# |string <b>id_token</b>    |  |string <b>username</b>|       |-----|
# |string refresh_token      |  |string <b>password</b>|       |-----|
# |string token_type         |  |----------------------|       `-----'
# |integer expires_in        |  `----------------------'
# |--------------------------|
# `--------------------------'

# http://boto3.readthedocs.io/en/latest/reference/services/cognito-identity.html#CognitoIdentity.Client.get_open_id_token
# https://stackoverflow.com/questions/28989054/amazon-aws-cognito-and-python-boto3-to-establish-aws-connection-and-upload-file
# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
def handler(request, context):
    cognito_idp_client = boto3.client('cognito-idp')

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info('http_post username=' + request_body['username'])
        cognito_app_client_id = get_cognito_app_client_id(cognito_idp_client,
                                                          cognito_user_pool_id=get('aws_user_pools_id'))

        # ##############################################################################################################
        # IF Cognito user pool was created by Amplify or Manually, it may not have an auth flow that works via python
        response = cognito_idp_client.describe_user_pool_client(
            UserPoolId=get('aws_user_pools_id'),
            ClientId=cognito_app_client_id
        )
        explicit_auth_flows = response['UserPoolClient']['ExplicitAuthFlows']
        explicit_auth_flows_count = len(explicit_auth_flows)
        if 'USER_PASSWORD_AUTH' not in explicit_auth_flows:
            explicit_auth_flows.extend('USER_PASSWORD_AUTH')
        if 'ADMIN_NO_SRP_AUTH' not in explicit_auth_flows:
            explicit_auth_flows.extend('ADMIN_NO_SRP_AUTH')

        if explicit_auth_flows_count != len(explicit_auth_flows):
            # add new auth flows to cognito user pool
            response = cognito_idp_client.update_user_pool_client(
                UserPoolId=get('aws_user_pools_id'),
                ClientId=cognito_app_client_id,
                ExplicitAuthFlows=[
                    'ADMIN_NO_SRP_AUTH',
                    'USER_PASSWORD_AUTH'
                ]
            )
        # ##############################################################################################################

        auth_response = cognito_idp_client.initiate_auth(
            ClientId=cognito_app_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': request_body['username'],
                'PASSWORD': request_body['password']
            }
        )

        logger.info('Auth successful')
        if "ChallengeName" in auth_response and auth_response["ChallengeName"] == "NEW_PASSWORD_REQUIRED":
            raise Exception("NEW_PASSWORD_REQUIRED")

        cognito_refresh_token = auth_response['AuthenticationResult']['RefreshToken']

        logger.info('return result tokens')
        return {"user": {},
                "access_token": auth_response['AuthenticationResult']['AccessToken'],
                "refresh_token": auth_response['AuthenticationResult']['RefreshToken'],
                "id_token": auth_response['AuthenticationResult']['IdToken'],
                "token_type": auth_response['AuthenticationResult']['TokenType'],
                "expires_in": auth_response['AuthenticationResult']['ExpiresIn']
                }

    return handle_request(request, context, http_post=http_post)
