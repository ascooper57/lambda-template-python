# -*- coding: utf-8 -*-

from os import getcwd

import boto3
from botocore.client import Config

from api.rdb.config import get
from api.rdb.model.db import tsvectorfield2string
from api.rdb.model.table_media import Media
from api.rdb.model.table_user_profile import User_profile
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                                                                                                                                                                ,------.
#                                                                                                                                                                |/media|
#                                                                                                                                                                |------|
#                                                                                                                                                                |------|
#                                                                                                                                                                `------'
#                                                                                                                                                                    |
#                                                                                                                                                                    |
#                                                                              ,--------------------------------------.   ,------------------------.   ,--------------------------.                      ,------------------------.
#                                                                              |POST /media                           |   |GET /media              |   |PUT /media                |   ,---------------.  |DELETE /media           |
#                                                                              |--------------------------------------|   |------------------------|   |--------------------------|   |OPTIONS /media |  |------------------------|
#                                                                              |.. body ..                            |   |.. query ..             |   |.. body ..                |   |---------------|  |.. query ..             |
#                                                                              |MediaUpdateForm <b>MediaUpdateForm</b>|   |string <b>media_uuid</b>|   |MediaForm <b>MediaForm</b>|   |.. responses ..|  |string <b>media_uuid</b>|
#                                                                              |.. responses ..                       |   |.. responses ..         |   |.. responses ..           |   |200: Empty     |  |.. responses ..         |
#                                                                              |200: MediaResponse                    |   |200: MediaResponse      |   |200: MediaResponse        |   |---------------|  |200: Empty              |
#                                                                              |--------------------------------------|   |------------------------|   |--------------------------|   `---------------'  |------------------------|
#                                                                              `--------------------------------------'   `------------------------'   `--------------------------'                      `------------------------'
#                                                                                                                                                                                                                     |
#                                                                      ,-----------------------------------------------------------------.                                                                            |
#                                                                      |MediaResponse                                                    |                                                                            |
#                                                                      |-----------------------------------------------------------------|   ,-----------------------------------------------------------------.      |
#                                                                      |integer id                                                       |   |MediaForm                                                        |      |
# ,-----------------------------------------------------------------.  |string media_uuid                                                |   |-----------------------------------------------------------------|      |
# |MediaUpdateForm                                                  |  |string username                                                  |   |string <b>media_uuid</b>                                         |      |
# |-----------------------------------------------------------------|  |                                                                 |   |string <b>email_id</b>                                           |   ,-----.
# |                                                                 |  |string subject {"Property", "Lodge", "Person", "Animal", "Other"}|   |                                                                 |   |Empty|
# |string subject {"Property", "Lodge", "Person", "Animal", "Other"}|  |object tags                                                      |   |string subject {"Property", "Lodge", "Person", "Animal", "Other"}|   |-----|
# |object tags                                                      |  |number latitude                                                  |   |object tags                                                      |   |-----|
# |integer likes                                                    |  |number longitude                                                 |   |number latitude                                                  |   `-----'
# |string description                                               |  |integer likes                                                    |   |number longitude                                                 |
# |-----------------------------------------------------------------|  |string description                                               |   |string media_created                                             |
# `-----------------------------------------------------------------'  |string updated_at                                                |   |integer likes                                                    |
#                                                                      |string created_at                                                |   |-----------------------------------------------------------------|
#                                                                      |-----------------------------------------------------------------|   `-----------------------------------------------------------------'
#                                                                      `-----------------------------------------------------------------'

def handler(request, context):
    # noinspection PyPep8Naming,PyUnusedLocal,PyProtectedMember
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        media_uuid = request_params['media_uuid']
        media = Media.get(Media.media_uuid == media_uuid)
        media.__data__['description'] = tsvectorfield2string(media.__data__['description'])
        return media.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        user_profile = User_profile.get(User_profile.username == request_body['username'])
        # noinspection PyUnresolvedReferences
        request_body['username'] = user_profile
        with Media.atomic():
            media, created = Media.get_or_create(media_uuid=request_body["media_uuid"], defaults=request_body)
            if created:
                logger.info("Media created")
            # noinspection PyProtectedMember
            return media.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_post")
        media_uuid = request_body['media_uuid']
        media = Media.get(Media.media_uuid == media_uuid)
        if "tags" in request_body:
            media.tags = request_body["tags"]
        if "likes" in request_body:
            media.likes = request_body["likes"]
        if "description" in request_body:
            media.description = request_body["description"]
        with media.atomic():
            media.save()
        return media.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_delete")

        try:
            with Media.atomic():
                query = Media.delete().where(Media.media_uuid == request_params["media_uuid"])
                response = query.execute()
        except Exception as ex:
            logger.error(str(ex))

        s3_client = boto3.client('s3', config=Config(signature_version='s3v4',
                                                     region_name=get('aws_cognito_region')))
        bucket_name = "media-%s" % get('aws_account_id')
        s3_client.delete_object(Bucket=bucket_name, Key=request_params["media_uuid"])
        return {}

    return handle_request(request, context, http_get=http_get, http_put=http_put, http_post=http_post,
                          http_delete=http_delete)
