# -*- coding: utf-8 -*-


from os import getcwd

import boto3

from api.rdb.utils.cognito import validate_uuid4
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request
from api.rdb.utils.sns import get_sns_attributes

logger = lambda_logger(__name__, getcwd())


#                                                        ,-------------.
#                                                        |/user/message|
#                                                        |-------------|
#                                                        |-------------|
#                                                        `-------------'
#
#
#  ,---------------------------.   ,------------------------------.   ,---------------------.
#  |GET /user/message          |   |PUT /user/message             |   |DELETE /user/message |  ,----------------.
#  |---------------------------|   |------------------------------|   |---------------------|  |OPTIONS /message|
#  |.. query ..                |   |.. body ..                    |   |.. query ..          |  |----------------|
#  |string <b>from_username</b>|   |MessageForm <b>MessageForm</b>|   |string <b>id</b>     |  |.. responses .. |
#  |string <b>to_username</b>  |   |.. responses ..               |   |.. responses ..      |  |200: Empty      |
#  |.. responses ..            |   |200: MessageResponse          |   |200: Empty           |  |----------------|
#  |200: MessageResponse       |   |------------------------------|   |---------------------|  `----------------'
#  |---------------------------|   `------------------------------'   `---------------------'
#  `---------------------------'                |
#                                               |
# ,----------------------------.                |
# |MessageResponse             |                |
# |----------------------------|   ,---------------------------.
# |string <b>from_username</b> |   |MessageForm                |
# |string <b>to_username</b>   |   |---------------------------|                     ,-----.
# |string <b>message</b>       |   |string <b>from_username</b>|                     |Empty|
# |string <b>sns_message_id</b>|   |string <b>message</b>      |                     |-----|
# |string id                   |   |string <b>to_username</b>  |                     |-----|
# |boolean sns                 |   |boolean <b>sms</b>         |                     `-----'
# |string updated_at           |   |---------------------------|
# |string created_at           |   `---------------------------'
# |----------------------------|
# `----------------------------'


# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        validate_uuid4(request_body['from_username'])
        validate_uuid4(request_body['to_username'])
        sns_client = boto3.client('sns')

        topic_attributes = get_sns_attributes(sns_client, request_body['to_username'])
        topic_arn = topic_attributes['TopicArn']
        if "sns" in request_body and request_body["sns"]:
            logger.info("TopicArn=" + topic_arn)
            response = sns_client.publish(Message=request_body['message'], TopicArn=topic_arn)
            request_body['sns_message_id'] = response['MessageId']
            logger.info("Create SMS Message=" + request_body['sns_message_id'])
            # noinspection PyProtectedMember
            return {'message_id': response['MessageId'], 'topic_arn': topic_arn}

    return handle_request(request, context, http_put=http_put)
