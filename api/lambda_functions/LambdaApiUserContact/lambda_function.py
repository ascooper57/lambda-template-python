# -*- coding: utf-8 -*-

import time
from os import getcwd

import boto3

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request
from api.rdb.utils.sns import get_sns_attributes

logger = lambda_logger(__name__, getcwd())


#                                                             ,-------------.
#                                                             |/user/contact|
#                                                             |-------------|
#                                                             |-------------|
#                                                             `-------------'
#
#
# ,-------------------------.  ,----------------------------------------.   ,--------------------.
# |GET /subscription        |  |PUT /subscription                       |   |DELETE /subscription|   ,---------------------.
# |-------------------------|  |----------------------------------------|   |--------------------|   |OPTIONS /subscription|
# |.. query ..              |  |.. body ..                              |   |.. query ..         |   |---------------------|
# |string <b>username</b>      |  |SubscriptionForm <b>SubscriptionForm</b> |   |string <b>id</b>    |  |.. responses ..   |
# |.. responses ..          |  |.. responses ..                         |   |.. responses ..     |   |200: Empty           |
# |200: SubscriptionResponse|  |200: SubscriptionResponse               |   |200: Empty          |   |---------------------|
# |-------------------------|  |----------------------------------------|   |--------------------|   `---------------------'
# `-------------------------'  `----------------------------------------'   `--------------------'
#                                                   |
#        ,----------------------.                   |
#        |SubscriptionResponse  |                   |
#        |----------------------|         ,-------------------.
#        |integer <b>id</b>     |         |SubscriptionForm   |                                 ,-----.
#        |string <b>topic_id</b>|         |-------------------|                                 |Empty|
#        |string <b>arn</b>     |         |string <b>username</b>|                              |-----|
#        |string updated_at     |         |string arn         |                                 |-----|
#        |string created_at     |         |-------------------|                                 `-----'
#        |----------------------|         `-------------------'
#        `----------------------'

# This is the lambda handler - it calls a general purpose service frame work that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    sns_client = boto3.client('sns')
    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_get")
        return get_sns_attributes(sns_client, request_params['username'])

    # https://bradmontgomery.net/blog/sending-sms-messages-amazon-sns-and-python/
    # phone  <-- number who'll receive an SMS message in e.I64 format. https://www.twilio.com/docs/glossary/what-e164
    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_put")
        username = request_body['username']
        phone_number = request_body['phone_number']
        # logger.info("username=%s" % username)
        try:
            topic_response = sns_client.create_topic(Name=username)
            subscribe_response = sns_client.subscribe(TopicArn=topic_response["TopicArn"],
                                                      Protocol='sms',
                                                      Endpoint=phone_number  # <-- number who'll receive an SMS message.
                                                      )
            # HACK for race condition for when topic_arn returned is actually usable
            time.sleep(5)
            # noinspection PyProtectedMember
            return {'topic_arn': topic_response['TopicArn']}
        except Exception as ex:
            logger.warning(str(ex))
            raise ex

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.info("http_delete")
        # noinspection PyUnresolvedReferences
        sns_client.delete_topic(TopicArn=request_params['topic_arn'])
        return {}

    return handle_request(request, context, http_get=http_get, http_put=http_put, http_delete=http_delete)
