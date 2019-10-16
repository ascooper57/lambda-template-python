# -*- coding: utf-8 -*-

import json

import boto3
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..utilities import invoke, get_lambda_test_data, get_lambda_fullpath
from ..conftest import get_secure_event

# noinspection PyUnusedLocal,PyTypeChecker
def test(empty_database, create_and_delete_user, create_login_session):
    if is_test():
        fullpath = get_lambda_fullpath("LambdaApiAwsBackup")
        event = get_lambda_test_data(fullpath)
        event, fullpath = get_secure_event("LambdaApiAwsBackup")

        # https://github.com/nficano/python-lambda
        response1 = invoke(fullpath, event)
        assert response1["statusCode"] == STATUS_OK
        assert "body" in response1
        body = response1['body']
        response_data = json.loads(body)
        assert 'duration' in response_data
        assert response_data['duration'] > 0.0

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiAwsBackup")
        # http://docs.python-requests.org/en/master/user/quickstart
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/aws/backup')
        response2 = requests.get(url, headers=event['headers'], params=event['queryStringParameters'])
        # "/backup should return Status \"OK\"")
        assert response2.status_code == STATUS_OK
        response_data = response2.json()
        assert 'duration' in response_data
        assert response_data['duration'] > 0.0
