# -*- coding: utf-8 -*-

import logging

import boto3
from boto3.session import Session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_api_url(rest_api_name, stage, endpoint):
    # type: (str, str, str) -> str
    # noinspection PyTypeChecker
    session = Session(region_name="us-east-1")
    credentials = session.get_credentials()

    apigateway_client = boto3.client("apigateway", aws_access_key_id=credentials.access_key,
                                     aws_secret_access_key=credentials.secret_key)
    url = 'https://%s.execute-api.us-east-1.amazonaws.com%s%s' % (
        get_rest_api_id(apigateway_client, rest_api_name),
        stage,
        endpoint
    )
    return url


def get_rest_api_id(apigateway_client, rest_api_name):
    # type: ('boto3.client("apigateway")', str) -> str
    """
    Get the Rest API ID from Rest API Name.

    :param apigateway_client:
    :param rest_api_name:
    :return: Rest API Id
    """
    # https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis
    logger.info("In get_rest_api_id: %s" % rest_api_name)
    response = apigateway_client.get_rest_apis(limit=500)
    rest_api_id = None
    # logger.info("response=" + str(response))
    for item in response['items']:
        if item['name'] == rest_api_name:
            rest_api_id = item['id']  # 'r1gzxipb32'
    return rest_api_id
