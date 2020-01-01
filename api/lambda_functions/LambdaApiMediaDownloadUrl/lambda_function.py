# -*- coding: utf-8 -*-

from os import getcwd

import boto3
from botocore.client import Config

from api.rdb.config import get
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                      ,------------------.
#                      |/media/downloadurl|
#                      |------------------|
#                      |------------------|
#                      `------------------'
#
#
# ,-----------------------------.
# |GET /media/downloadurl       |  ,--------------------------.
# |-----------------------------|  |OPTIONS /media/downloadurl|
# |.. query ..                  |  |--------------------------|
# |string <b>media_uuid</b>     |  |.. responses ..           |
# |.. responses ..              |  |200: Empty                |
# |200: MediaDownloadUrlResponse|  |--------------------------|
# |-----------------------------|  `--------------------------'
# `-----------------------------'                |
#                |                               |
#   ,------------------------.                   |
#   |MediaDownloadUrlResponse|                ,-----.
#   |------------------------|                |Empty|
#   |string <b>url</b>       |                |-----|
#   |------------------------|                |-----|
#   `------------------------'                `-----'

# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    logger.info('entered:' + context.function_name)

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        s3_client = boto3.client('s3', config=Config(signature_version='s3v4',
                                                     region_name=get('aws_region_name')))
        bucket_name = "media-%s" % get('aws_account_id')
        s3_client.create_bucket(ACL='private', Bucket=bucket_name)
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': request_params['media_uuid']
            }
        )
        logger.info(url)
        return {"url": url}

    return handle_request(request, context, http_get=http_get)
