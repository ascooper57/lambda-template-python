# -*- coding: utf-8 -*-

import json

import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..utilities import invoke, get_lambda_test_data, get_lambda_fullpath


# noinspection PyUnusedLocal,PyTypeChecker
def test():
    if is_test():
        fullpath = get_lambda_fullpath("LambdaApiHealth")
        event = get_lambda_test_data(fullpath)
        # https://github.com/nficano/python-lambda
        # noinspection PyTypeChecker
        response1 = invoke(fullpath, event)
        assert response1 is not None
        assert response1['statusCode'] == STATUS_OK
        # dict'{"health": "OK", "statusCode": 200, "headers": {"Content-Type": "application/json"}}'
        response_data = json.loads(response1['body'])
        assert response_data['health'] == "OK"

    elif is_production():
        event = get_lambda_test_data(get_lambda_fullpath("LambdaApiHealth"))
        # http://docs.python-requests.org/en/master/user/quickstart
        url = get_api_url('API', '/v1', '/health')
        response2 = requests.get(url, params=event['queryStringParameters'])
        assert response2 is not None
        assert response2.status_code == STATUS_OK
        response_data = response2.json()
        # dict'{"health": "OK"}'
        assert response_data['health'] == "OK"
