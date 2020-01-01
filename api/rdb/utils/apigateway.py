# -*- coding: utf-8 -*-

import logging

from api.rdb.config import get

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_api_url(apigateway_client, rest_api_name, stage, endpoint):
    # type: ('boto3.client("apigateway")', str, str, str) -> str
    return 'https://%s.execute-api.%s.amazonaws.com%s%s' % (
        get_rest_api_id(apigateway_client, rest_api_name),
        get('aws_region_name'),
        stage,
        endpoint
    )


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
            rest_api_id = item['id']  # 'as2edhw8s7'
    return rest_api_id
