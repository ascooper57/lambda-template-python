# -*- coding: utf-8 -*-

import json

import requests
import yaml

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK
from ..utilities import invoke, get_lambda_test_data, get_lambda_fullpath


# noinspection PyUnusedLocal,PyTypeChecker
def test():
    if is_test():
        fullpath = get_lambda_fullpath("LambdaApiSwagger")
        event = get_lambda_test_data(fullpath)
        # noinspection PyTypeChecker
        response1 = invoke(fullpath, event)
        assert response1['statusCode'] == STATUS_OK
        assert len(response1['body'])
        assert json.loads(response1['body'])

        payload = {"httpMethod": "GET", "queryStringParameters": {"format": 'yaml'}}
        # noinspection PyTypeChecker
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        assert len(response2['body'])
        assert yaml.load(response2['body'], Loader=yaml.SafeLoader)

    elif is_production():
        fullpath = get_lambda_fullpath("LambdaApiSwagger")
        event = get_lambda_test_data(fullpath)
        url = get_api_url('API', '/v1', '/swagger')
        response3 = requests.get(url, params=event['queryStringParameters'])
        assert response3.status_code == STATUS_OK
        assert len(response3.text)
        assert json.loads(response3.text)
        with open("API.json", "w") as text_file:
            text_file.write(response3.text)

        event['queryStringParameters']['format'] = "yaml"
        response4 = requests.get(url, params=event['queryStringParameters'])
        assert response4.status_code == STATUS_OK
        assert len(response4.text)
        assert yaml.load(response4.text, Loader=yaml.SafeLoader)
        with open("API.yaml", "w") as text_file:
            text_file.write(response4.text)
