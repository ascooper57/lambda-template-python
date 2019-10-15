# -*- coding: utf-8 -*-

from os import getcwd
from time import sleep

import boto3

from api.rdb.config import get, is_test
from api.rdb.utils.cognito import get_cognito_app_client_id
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


def handler(request, context):
    cognito_idp_client = boto3.client('cognito-idp')

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        # Don't Email when new user is provisioned in Cognito if is_test()
        message_action = 'SUPPRESS' if is_test() else 'RESEND'
        cognito_user = user_persist(cognito_idp_client,
                                    get('aws_user_pools_id'),
                                    request_body,
                                    True,
                                    ['EMAIL'],
                                    message_action)
        cognito_user = cognito_idp_client.admin_get_user(UserPoolId=get('aws_user_pools_id'),
                                                         Username=cognito_user['Username'])
        return remove_cruft(cognito_user)

    # noinspection PyPep8Naming,PyUnusedLocal,PyBroadException
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_delete")
        if request_params and 'force' in request_params:
            logger.info(request_params['force'])
        # if test, delete the user
        # if production, de-activate
        logger.info("http_delete in %s mode" % 'test' if is_test() else 'production')
        # disable user in Cognito
        if is_test() or "force" in request_params:
            try:
                cognito_idp_client.admin_disable_user(UserPoolId=get('aws_user_pools_id'),
                                                      Username=request_params['username'])
                sleep(2)
            except cognito_idp_client.exceptions.UserNotFoundException as ex:
                return {}

        if is_test() or "force" in request_params:
            logger.info("Deleting user %s for real" % request_params['username'])
            cognito_idp_client.admin_delete_user(UserPoolId=get('aws_user_pools_id'),
                                                 Username=request_params['username'])
            logger.info("Deleted user from Cognito")
        return {}

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        cognito_user = cognito_idp_client.admin_get_user(UserPoolId=get('aws_user_pools_id'),
                                                         Username=request_params['username'])
        return remove_cruft(cognito_user)

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_post")
        cognito_user = cognito_idp_client.admin_get_user(UserPoolId=get('aws_user_pools_id'),
                                                         Username=request_body['username'])

        if "cognito_user_pool_app_client_id" in request_body:
            cognito_app_client_id = request_body['cognito_user_pool_app_client_id']
        else:
            cognito_app_client_id = get_cognito_app_client_id(cognito_idp_client,
                                                              cognito_user_pool_id=get('aws_user_pools_id'))

        # TODO: enable ADMIN_NO_SRP_AUTH and USER_PASSWORD_AUTH auth flows
        if 'newpassword' in request_body:
            # noinspection PyBroadException
            auth_response = cognito_idp_client.admin_initiate_auth(
                UserPoolId=get('aws_user_pools_id'),
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': cognito_user['Username'],
                    'PASSWORD': request_body['password']
                },
                ClientId=cognito_app_client_id
            )
            # https://github.com/capless/warrant/issues/14
            tokens = cognito_idp_client.respond_to_auth_challenge(
                ClientId=cognito_app_client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=auth_response['Session'],  # 'session_string_from_first_challenge_response',
                ChallengeResponses={
                    'NEW_PASSWORD': request_body['newpassword'],
                    'USERNAME': request_body['username']
                }
            )
            logger.info('newpassword successful, return result tokens')

        cognito_user = remove_cruft(cognito_user)
        return cognito_user

    return handle_request(request, context, http_get=http_get, http_put=http_put, http_delete=http_delete,
                          http_post=http_post)


# https://console.aws.amazon.com/cognito/pool/edit/?region=us-east-1&id=us-east-1:e55c591f-df3e-4161-8d54-0fd7e38dfd91


# http://boto3.readthedocs.io/en/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_create_user
# noinspection PyUnusedLocal
def user_persist(cognito_idp_client, cognito_user_pool_id, request_body, email_verified, delivery_medium,
                 message_action):
    from api.rdb.model.table_user_profile import User_profile

    # noinspection PyBroadException
    try:
        # need this step after user successful login (means that they changed default password successfully
        cognito_user = cognito_idp_client.admin_get_user(UserPoolId=cognito_user_pool_id,
                                                         Username=request_body['username'])
        if 'UserStatus' in cognito_user and cognito_user['UserStatus'] == 'FORCE_CHANGE_PASSWORD':
            with User_profile.atomic():
                User_profile.get_or_create(username=cognito_user['Username'])
            return cognito_user
    except cognito_idp_client.exceptions.UserNotFoundException as ex:
        pass

    if is_test():
        # Don't Email when new user is provisioned in Cognito
        cognito_user = cognito_idp_client.admin_create_user(
            UserPoolId=cognito_user_pool_id,
            Username=request_body["username"],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': request_body["email"]
                },
                {
                    'Name': 'email_verified',
                    'Value': 'True'
                },
                {
                    'Name': 'phone_number',
                    'Value': request_body["phone_number"]
                },
                {
                    'Name': 'phone_number_verified',
                    'Value': 'True'
                }
            ],
            TemporaryPassword=request_body["password"],
            ForceAliasCreation=email_verified,
            MessageAction=message_action,
            DesiredDeliveryMediums=delivery_medium
        )
    else:
        # Send Email when new user is provisioned in Cognito with temp password
        cognito_user = cognito_idp_client.admin_create_user(
            UserPoolId=cognito_user_pool_id,
            Username=request_body["username"],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': request_body["email"]
                },
                {
                    'Name': 'email_verified',
                    'Value': 'True'
                },
                {
                    'Name': 'phone_number',
                    'Value': request_body["phone_number"]
                },
                {
                    'Name': 'phone_number_verified',
                    'Value': 'True'
                }
            ],
            TemporaryPassword=request_body["password"],
            ForceAliasCreation=email_verified,
            DesiredDeliveryMediums=delivery_medium
        )

    with User_profile.atomic():
        request_body = {'username': cognito_user['User']['Username']}
        # user_profile = User_profile.create(**request_body)
        User_profile.get_or_create(username=request_body['username'], defaults=request_body)

    return cognito_user['User']


def remove_cruft(cognito_user):
    cu = cognito_user
    # cu.pop('UserAttributes', None)
    cu.pop('ResponseMetadata', None)
    return cu
