# -*- coding: utf-8 -*-

import boto3
import json
import requests

from api.rdb.config import is_test, is_production
from ..utilities import invoke
from api.rdb.utils.service_framework import STATUS_OK, STATUS_NOT_FOUND
from api.rdb.utils.apigateway import get_api_url
from ..conftest import get_secure_event

# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user, create_login_session):
    cognito_idp_client = boto3.client('cognito-idp')
    event, fullpath = get_secure_event("LambdaApiUserProfile")
    response1 = invoke(fullpath, event)
    assert response1['statusCode'] == STATUS_OK
    response_data = json.loads(response1['body'])
    username = response_data['username']
    if is_test():
        event, fullpath = get_secure_event("LambdaApiMedia")
        event['body']['username'] = username
        payload = {"httpMethod": "PUT", "body": event['body']}
        # noinspection PyTypeChecker
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK

        payload = {"httpMethod": "GET", "queryStringParameters": {"media_uuid": event['body']['media_uuid']}}
        # noinspection PyTypeChecker
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK
        response_data = json.loads(response3['body'])
        assert response_data['likes'] == event['body']['likes']

        event, fullpath = get_secure_event("LambdaApiMedia")
        new_likes = event['body']['likes'] + 1
        event['body']['likes'] = new_likes
        payload = {"httpMethod": "POST", "body": event['body']}
        # noinspection PyTypeChecker
        response4 = invoke(fullpath, payload)
        assert response4['statusCode'] == STATUS_OK

        payload = {"httpMethod": "GET", "queryStringParameters": {"media_uuid": event['body']['media_uuid']}}
        # noinspection PyTypeChecker
        response5 = invoke(fullpath, payload)
        assert response5['statusCode'] == STATUS_OK
        response_data = json.loads(response5['body'])
        assert response_data['likes'] == new_likes

        payload = {"httpMethod": "DELETE", "queryStringParameters": {"media_uuid": event['body']['media_uuid']}}
        # noinspection PyTypeChecker
        response6 = invoke(fullpath, payload)
        assert response6['statusCode'] == STATUS_OK

    elif is_production():
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/media')
        event, fullpath = get_secure_event("LambdaApiMedia")
        event['body']['username'] = username
        response7 = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response7.status_code == STATUS_OK
        response_data = json.loads(response7.text)

        media_uuid = response_data['media_uuid']
        response8 = requests.get(url, headers=event['headers'], params={"media_uuid": media_uuid})
        assert response8.status_code == STATUS_OK

        event['body']['likes'] = 4
        event['body']['media_uuid'] = media_uuid
        response9 = requests.post(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response9.status_code == STATUS_OK

        response10 = requests.delete(url, headers=event['headers'], params={"media_uuid": media_uuid})
        assert response10.status_code == STATUS_OK

        # negative test
        response11 = requests.get(url, headers=event['headers'], params={"media_uuid": media_uuid})
        assert response11.status_code == STATUS_NOT_FOUND
