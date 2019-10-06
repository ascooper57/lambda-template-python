# -*- coding: utf-8 -*-

import json

import boto3
import requests

from api.rdb.config import is_test, is_production
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK, STATUS_OK_NO_CONTENT
from ..conftest import get_secure_event
from ..utilities import invoke


# https://pypkg.com/pypi/botocore/f/tests/integration/test_s3.py
# https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html
# noinspection PyUnusedLocal
def test_local(empty_database, fixture_directory, create_and_delete_user, create_login_session):
    if is_test():
        event, fullpath = get_secure_event("LambdaApiMediaUploadUrl")
        payload = {"httpMethod": "GET"}
        # noinspection PyTypeChecker
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        data = json.loads(response2['body'])
        assert len(data) == 2
        media_uuid = data['media_uuid']
        assert len(media_uuid)

        url = data['url']
        assert len(url)
        # headers = {'Content-Type': 'image/jpeg'}
        # https://stackoverflow.com/questions/8710456/reading-a-binary-file-with-python
        with open(fixture_directory + "/image.jpeg", mode='rb') as file:  # b is important -> binary
            file_content = file.read()
        # files = {"file": open(fixture_directory + "/image.jpeg", 'rb')}
        files = {"file": file_content}
        response3 = requests.put(url, files=files)
        assert response3.status_code == STATUS_OK or response3.status_code == STATUS_OK_NO_CONTENT

        event, fullpath = get_secure_event("LambdaApiMediaDownloadUrl")
        event["queryStringParameters"]["media_uuid"] = data['media_uuid']
        payload = {"httpMethod": "GET", "queryStringParameters": event["queryStringParameters"]}
        # noinspection PyTypeChecker
        response4 = invoke(fullpath, payload)
        assert response4['statusCode'] == STATUS_OK
        url = json.loads(response4['body'])['url']

        response5 = requests.get(url)
        assert response5.status_code == STATUS_OK

        event, fullpath = get_secure_event("LambdaApiMedia")
        payload = {"httpMethod": "DELETE", "queryStringParameters": {"media_uuid": media_uuid}}
        # noinspection PyTypeChecker
        response3 = invoke(fullpath, payload)
        assert response3['statusCode'] == STATUS_OK

    elif is_production():
        event, fullpath = get_secure_event("LambdaApiMediaUploadUrl")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/media/uploadurl')
        response6 = requests.get(url, headers=event['headers'])
        assert response6.status_code == STATUS_OK
        data = json.loads(response6.text)

        s3_url = data['url']
        assert len(s3_url)

        media_uuid = data['media_uuid']
        assert len(media_uuid)

        # headers = {'Content-Type': 'image/jpeg'}
        files = {"file": open(fixture_directory + "/image.jpeg", 'rb')}

        # response = requests.post(s3_url, data=fields, files=open(fixture_directory + "/image.jpeg", 'rb'))
        response7 = requests.put(s3_url, files=files)
        assert response7.status_code == STATUS_OK or response7.status_code == STATUS_OK_NO_CONTENT

        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/media/downloadurl')
        # noinspection PyTypeChecker
        response8 = requests.get(url, headers=event['headers'], params={"media_uuid": media_uuid})
        assert response8.status_code == STATUS_OK
        data = json.loads(response8.text)

        response9 = requests.get(data['url'])
        assert response9.status_code == STATUS_OK

        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/media')
        response9 = requests.delete(url, headers=event['headers'], params={"media_uuid": media_uuid})
        assert response9.status_code == STATUS_OK
