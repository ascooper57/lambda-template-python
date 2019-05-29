# -*- coding: utf-8 -*

from os import getcwd

import boto3

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#              ,--------.
#              |/swagger|
#              |--------|
#              |--------|
#              `--------'
#
#
# ,---------------.  ,----------------.
# |GET /swagger   |  |OPTIONS /swagger|
# |---------------|  |----------------|
# |.. responses ..|  |.. responses .. |
# |200: Empty     |  |200: Empty      |
# |---------------|  |----------------|
# `---------------'  `----------------'
#
#                ,-----.
#                |Empty|
#                |-----|
#                |-----|
#                `-----'

# request – AWS Lambda uses this parameter to pass in event data to the handler.
# This parameter is usually of the Python dict type.
# It can also be list, str, int, float, or NoneType type.
# Example: message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])
def handler(request, context):
    # noinspection PyPep8Naming,PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        apigateway_client = boto3.client('apigateway')
        content_type = "json"
        if request_params is not None:
            if "format" in request_params:
                content_type = request_params['format'].lower()
        rest_api_id = None
        response = apigateway_client.get_rest_apis(limit=500)
        # https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis
        for item in response['items']:
            if item['name'].lower() == "API".lower():
                rest_api_id = item['id']  # 'r1gzxipb32'
        logger.info("rest api id=%s" % rest_api_id)
        response = apigateway_client.get_export(
            restApiId=rest_api_id,
            stageName='v1',
            exportType='swagger',
            parameters={
            },
            accepts='application/%s' % content_type
        )
        # https://gist.github.com/pgolding/9083a6f3590067e3ffe694c947ef90a3
        swagger = response['body'].read().decode("utf-8")
        return swagger

    return handle_request(request, context, http_get=http_get)
