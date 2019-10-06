# -*- coding: utf-8 -*-
from os import getcwd

import boto3
from botocore.client import Config

from api.rdb.config import get
from api.rdb.model.table_media import Media
from api.rdb.model.table_user_profile import User_profile
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#                                                                                  ,------------.
#                                                                                  |/media/query|
#                                                                                  |------------|
#                                                                                  |------------|
#                                                                                  `------------'
#
#
#                                                     ,------------------------------------.
#                                                     |POST /media/query                   |   ,--------------------.
#                                                     |------------------------------------|   |OPTIONS /media/query|
#                                                     |.. body ..                          |   |--------------------|
#                                                     |MediaQueryForm <b>MediaQueryForm</b>|   |.. responses ..     |
#                                                     |.. responses ..                     |   |200: Empty          |
#                                                     |200: MediaQueryResponse             |   |--------------------|
#                                                     |------------------------------------|   `--------------------'
#                                                     `------------------------------------'              |
#                                                                                                         |
# ,-----------------------------------------------------------------.                                     |
# |MediaQueryForm                                                   |                                     |
# |-----------------------------------------------------------------|                                     |
# |string username                                                  |  ,------------------.            ,-----.
# |object tags                                                      |  |MediaQueryResponse|            |Empty|
# | integer likes                                                   |  |------------------|            |-----|
# |                                                                 |  |------------------|            |-----|
# |                                                                 |  `------------------'            `-----'
# |-----------------------------------------------------------------|
# `-----------------------------------------------------------------'


# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    # from api.rdb.model.foobar import FOOBAR
    logger.info("Entered LambdaApiMediaQuery handler")

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> list
        logger.info("http_post")
        cognito_idp_client = boto3.client('cognito-idp')
        user_profile = User_profile.get(User_profile.username == request_body['username'])

        # noinspection PyUnresolvedReferences
        s3_client = boto3.client('s3', config=Config(signature_version='s3v4',
                                                     region_name=get('aws_cognito_region')))
        # {
        #     "username_id": "TESTER1",
        #     "media_uuid": "fffe57fe-a60b-4374-8c35-97abe629afbb",
        #     "tags": {"species": "Whitetail", "size": "10 point"},
        #     "latitude": 38.8966,
        #     "longitude": 121.0769,
        #     "media_created": "2004-10-19 10:23:54",
        # }

        where = []
        if request_body:
            if "tags" in request_body:
                for k, v in request_body["tags"].items():
                    where += ["tags->'%s' = '%s'" % (k, v)]

            if "likes" in request_body:
                where += ["likes >= %i" % request_body["likes"]]

            if "username" in request_body:  #
                # noinspection PyUnresolvedReferences
                where += ["username_id = '%s'" % user_profile.id]

        if where:
            sql = "select * from media where %s order by media_created desc;" % " and ".join(where)
        else:
            sql = "select * from media;"

        logger.info(sql)
        urls = []
        bucket_name = "media-%s" % get('aws_account_id')
        for media in Media.raw(sql):
            logger.info(media)
            url = s3_client.generate_presigned_url(ClientMethod='get_object',
                                                   Params={'Bucket': bucket_name,
                                                           'Key': media.media_uuid.hex}
                                                   )
            urls += [url]

        logger.info(urls)
        return urls

        # return result.__data__

    return handle_request(request, context, http_post=http_post, http_get=http_post)
