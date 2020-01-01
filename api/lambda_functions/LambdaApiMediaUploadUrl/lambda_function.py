# -*- coding: utf-8 -*-
import uuid
from os import getcwd

import boto3
from botocore.client import Config

from api.rdb.config import get
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                     ,----------------.
#                     |/media/uploadurl|
#                     |----------------|
#                     |----------------|
#                     `----------------'
#
#
# ,---------------------------.
# |GET /media/uploadurl       |  ,------------------------.
# |---------------------------|  |OPTIONS /media/uploadurl|
# |.. query ..                |  |------------------------|
# |string method              |  |.. responses ..         |
# |.. responses ..            |  |200: Empty              |
# |200: MediaUploadUrlResponse|  |------------------------|
# |---------------------------|  `------------------------'
# `---------------------------'               |
#               |                             |
#   ,----------------------.                  |
#   |MediaUploadUrlResponse|               ,-----.
#   |----------------------|               |Empty|
#   |object post           |               |-----|
#   |string media_uuid     |               |-----|
#   |----------------------|               `-----'
#   `----------------------'

# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    # noinspection PyPep8Naming,PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        s3_resource = boto3.resource('s3', region_name=get('aws_region_name'))
        s3_client = boto3.client('s3', config=Config(signature_version='s3v4',
                                                     region_name=get('aws_region_name')))
        bucket_name = "media-%s" % get('aws_account_id')
        logger.info("before create bucket")
        s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
        logger.info("before generate_presigned_url")
        key = str(uuid.uuid4())
        # Generate the URL to get 'key-name' from 'bucket-name'
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            HttpMethod="put"
        )
        return {"url": url, "media_uuid": key}

    return handle_request(request, context, http_get=http_get)
