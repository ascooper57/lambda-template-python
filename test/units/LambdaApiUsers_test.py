# -*- coding: utf-8 -*-

import json

import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..utilities import invoke, get_lambda_test_data, get_lambda_fullpath


# noinspection PyUnusedLocal,PyTypeChecker
def test(empty_database, create_and_delete_user):
    if is_test():
        fullpath = get_lambda_fullpath("LambdaApiUsers")
        event = get_lambda_test_data(fullpath)
        # https://github.com/nficano/python-lambda
        response1 = invoke(fullpath, event)
        assert response1 is not None
        assert response1["statusCode"] == STATUS_OK
        assert "body" in response1
        body = response1['body']
        response_data = json.loads(body)
        assert response_data
        assert len(response_data)

    elif is_production():
        fullpath = get_lambda_fullpath("LambdaApiUsers")
        event = get_lambda_test_data(fullpath)
        url = get_api_url('API', '/v1', '/users')
        # http://docs.python-requests.org/en/master/user/quickstart
        response3 = requests.get(url, params=event['queryStringParameters'])
        assert response3.status_code == STATUS_OK
        response_data = response3.json()
        assert response_data
        assert len(response_data)
