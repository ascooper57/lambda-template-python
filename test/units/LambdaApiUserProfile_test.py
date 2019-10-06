# -*- coding: utf-8 -*-

import boto3
import json
import requests

from api.rdb.config import is_test, is_production
from ..utilities import invoke
from api.rdb.utils.service_framework import STATUS_OK
from api.rdb.utils.apigateway import get_api_url
from ..conftest import get_secure_event

# noinspection PyUnusedLocal,PyTypeChecker
def test(empty_database, create_and_delete_user, create_login_session):
    cognito_idp_client = boto3.client('cognito-idp')
    if is_test():
        event, fullpath = get_secure_event("LambdaApiUserProfile")
        response1 = invoke(fullpath, event)
        assert response1['statusCode'] == STATUS_OK
        response_data = json.loads(response1['body'])
        for k in event['body']:
            if k in response_data:
                assert event['body'][k] == response_data[k]

        payload = {"httpMethod": "GET", "queryStringParameters": {"username": event['body']['username']}}
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        response_data = json.loads(response2['body'])

        # noinspection PyShadowingBuiltins
        id = response_data['id']
        payload = {"httpMethod": "DELETE", "queryStringParameters": {"id": id}}
        # noinspection PyTypeChecker
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiUserProfile")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/profile')
        response4 = requests.post(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response4.status_code == STATUS_OK
        response_data = json.loads(response4.text)
        for k in event['body']:
            if k in response_data:
                assert event['body'][k] == response_data[k]

        response5 = requests.get(url, headers=event['headers'], params=event['body'])
        assert response5.status_code == STATUS_OK
        response_data = json.loads(response5.text)
        assert response_data

        # noinspection PyShadowingBuiltins
        event['body']['id'] = response_data["id"]
        response6 = requests.delete(url, headers=event['headers'], params=event['body'])
        assert response6.status_code == STATUS_OK
