# -*- coding: utf-8 -*-

import json
import boto3
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.helpers import invoke, get_lambda_test_data, get_lambda_fullpath
from api.rdb.utils.service_framework import STATUS_OK
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.cognito import get_cognito_username_id

# noinspection PyUnusedLocal,PyTypeChecker
def test(empty_database, create_and_delete_user):
    if is_test():
        # new user, FORCE_CHANGE_PASSWORD required
        force_change_password()

        # new user, fully authenticated use new password
        fullpath = get_lambda_fullpath("LambdaApiUserSignIn")
        event = get_lambda_test_data(fullpath)
        # https://github.com/nficano/python-lambda
        # noinspection PyTypeChecker
        response1 = invoke(fullpath, event)
        assert response1 is not None  # "/user/signin should return Status \"OK\"")
        assert response1["statusCode"] == STATUS_OK
        assert "body" in response1
        body = response1['body']
        response_data = json.loads(body)
        validate_response(response_data)

    elif is_production():
        force_change_password()
        # new user, fully authenticated use new password via API Gateway
        event = get_lambda_test_data(get_lambda_fullpath("LambdaApiUserSignIn"))
        # http://docs.python-requests.org/en/master/user/quickstart
        url = get_api_url('API', '/v1', '/user/signin')
        response3 = requests.post(url, headers=event['headers'], data=json.dumps(event['body']))
        response_data = response3.json()
        assert response3.status_code == STATUS_OK
        validate_response(response_data)


def validate_response(response_data):
    assert "user" in response_data
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert "id_token" in response_data
    assert "token_type" in response_data
    assert "expires_in" in response_data
    assert response_data["token_type"] == "Bearer"
    assert response_data["expires_in"] == 3600


def force_change_password():
    # new user, FORCE_CHANGE_PASSWORD required
    fullpath = get_lambda_fullpath("LambdaApiUserSignUp")
    event = get_lambda_test_data(fullpath)
    # Update user tester1@praktikos.com
    cognito_idp_client = boto3.client('cognito-idp')
    event['body']['username'] = get_cognito_username_id(cognito_idp_client,
                                       event['body']['email'],
                                       event['body']['cognito_user_pool_id'])
    event['body'].pop('email', None)
    payload = {"httpMethod": "POST", "body": event['body']}
    response1 = invoke(fullpath, payload)
    assert response1['statusCode'] == STATUS_OK
    assert len(response1['body'])
    response_data = json.loads(response1['body'])
    assert response_data['Username']
    assert event['body']['username'] == response_data['Username']
    assert 'UserCreateDate' in response_data
    assert 'UserLastModifiedDate' in response_data
    assert 'Enabled' in response_data
    assert 'UserStatus' in response_data
