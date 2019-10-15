# -*- coding: utf-8 -*-


import json

import boto3
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..conftest import get_secure_event
from ..utilities import invoke

# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user, create_login_session, create_user_contact):
    if is_test():
        event, fullpath = get_secure_event("LambdaApiUserMessage")
        event['body']["sns"] = True
        response1 = invoke(fullpath, event)
        assert response1['statusCode'] == STATUS_OK
        response_data = json.loads(response1['body'])
        assert response_data
        assert 'message_id' in response_data
        assert len(response_data['message_id']) >= 32
        assert 'topic_arn' in response_data
        topic_arn = response_data['topic_arn']

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiUserProfile")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/profile')
        response = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response.status_code == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiUserMessage")
        event['body']["sns"] = True
        # http://docs.python-requests.org/en/master/user/quickstart
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/message')
        response4 = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response4.status_code == STATUS_OK
        response_data = json.loads(response4.text)
        assert response_data
        assert "message_id" in response_data
        assert len(response_data['message_id']) > 32

        event, fullpath = get_secure_event("LambdaApiUserContact")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/contact')
        response5 = requests.get(url, headers=event['headers'], params=event['body'])
        assert response5.status_code == STATUS_OK
        response_data = json.loads(response5.text)
        # assert any(event['username'] in s['username'] for s in data)

        response6 = requests.delete(url, headers=event['headers'], params={"topic_arn": response_data['TopicArn']})
        assert response6.status_code == STATUS_OK
        response_data = json.loads(response6.text)
