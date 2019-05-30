# -*- coding: utf-8 -*-

import json

import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..conftest import get_secure_event
from ..utilities import invoke


# noinspection PyUnusedLocal,PyTypeChecker
def test(empty_database, create_and_delete_user, create_login_session):
    if is_test():
        event, fullpath = get_secure_event("LambdaApiSamplePython")
        payload = event
        response1 = invoke(fullpath, payload)
        assert response1['statusCode'] == STATUS_OK
        response_data = json.loads(response1['body'])
        assert response_data
        if isinstance(response_data, dict):
            for k in event['body']:
                if k in response_data:
                    assert event['body'][k] == response_data[k]

        payload = {"httpMethod": "GET",
                   "queryStringParameters": {"index_key_example": event['body']['index_key_example']}}
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        response_data = json.loads(response2['body'])

        # noinspection PyShadowingBuiltins
        id = response_data[0]['id']
        payload = {"httpMethod": "DELETE", "queryStringParameters": {"id": id}}
        # noinspection PyTypeChecker
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiSamplePython", aws=True)
        url = get_api_url('API', '/v1', '/sample')

        response4 = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        assert response4.status_code == STATUS_OK
        response_data = json.loads(response4.text)
        assert response_data

        response5 = requests.get(url, headers=event['headers'],
                                 params={"index_key_example": event['body']['index_key_example']})
        assert response5.status_code == STATUS_OK
        response_data = json.loads(response5.text)
        assert response_data

        # noinspection PyShadowingBuiltins
        id = response_data[0]["id"]
        response6 = requests.delete(url, headers=event['headers'], params={"id": id})
        assert response6.status_code == STATUS_OK
