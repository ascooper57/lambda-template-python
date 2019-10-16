# -*- coding: utf-8 -*-

import json

import boto3
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK, STATUS_NOT_FOUND
from ..conftest import get_secure_event
from ..utilities import invoke


# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user, create_login_session):
    cognito_idp_client = boto3.client('cognito-idp')
    if is_test():
        event, fullpath = get_secure_event("LambdaApiUserBlocked")
        response1 = invoke(fullpath, event)
        assert response1['statusCode'] == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiUserBlocked")
        payload = {"httpMethod": "GET",
                   "queryStringParameters": event['body']}
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        response_data = json.loads(response2['body'])
        assert response_data['blocked']

        payload = {"httpMethod": "DELETE",
                   "queryStringParameters": {"id": response_data["id"]}}
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK

        # negative test
        payload = {"httpMethod": "GET",
                   "queryStringParameters": {"recipient_username": "x@y.com",
                                             "blocked_username": event['body']['blocked_username']}}
        response4 = invoke(fullpath, payload)
        assert response4['statusCode'] == STATUS_NOT_FOUND
        response_data = json.loads(response4['body'])
        assert response_data['Message']

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiUserBlocked")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/blocked')

        response5 = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response5.status_code == STATUS_OK

        response6 = requests.get(url, headers=event['headers'], params=event['body'])
        assert response6.status_code == STATUS_OK
        response_data = json.loads(response6.text)

        response7 = requests.delete(url, headers=event['headers'], params={"id": response_data["id"]})
        assert response7.status_code == STATUS_OK

        # negative test
        event['body']['recipient_username'] = "x@y.com"
        response8 = requests.get(url,
                                 headers=event['headers'],
                                 params=event['body'])
        assert response8.status_code == STATUS_NOT_FOUND
        response_data = json.loads(response8.text)
        assert response_data
