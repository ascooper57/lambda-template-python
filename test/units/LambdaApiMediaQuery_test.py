# -*- coding: utf-8 -*-


import boto3
import json
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from ..utilities import invoke
from api.rdb.utils.service_framework import STATUS_OK
from ..conftest import get_secure_event


# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user, create_login_session):
    if is_test():
        event, fullpath = get_secure_event("LambdaApiUserProfile")
        response1 = invoke(fullpath, event)
        assert response1['statusCode'] == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiMedia")
        payload = {"httpMethod": "PUT", "body": event['body']}
        # noinspection PyTypeChecker
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiMediaQuery")
        payload = {"httpMethod": "POST", "body": event['body']}
        # noinspection PyTypeChecker
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiMediaQuery")
        event['body'].pop('description', None)
        event['body'].pop('tags', None)
        event['body'].pop('likes', None)
        payload = {"httpMethod": "POST", "body": event['body']}
        # noinspection PyTypeChecker
        response4 = invoke(fullpath, payload)
        assert response4['statusCode'] == STATUS_OK

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiMediaQuery")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/media/query')
        response5 = requests.post(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response5.status_code == STATUS_OK
        data = json.loads(response5.text)
        # assert data
        # assert len(data)
