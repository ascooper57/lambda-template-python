# -*- coding: utf-8 -*-


from os import getcwd

from api.rdb.utils.lambda_logger import lambda_logger

logger = lambda_logger(__name__, getcwd())


def get_sns_attributes(sns_client, username):
    # type: ('boto3.client("sns")', str) -> dict
    logger.info("http_get")
    next_token = ""
    topics = sns_client.list_topics(NextToken=next_token)
    for topic in topics['Topics']:
        parts = topic['TopicArn'].split(":")
        if parts[len(parts) - 1] == username:
            response = sns_client.get_topic_attributes(TopicArn=topic['TopicArn'])
            return response['Attributes']
    raise Exception("TopicArn for username: %s not found" % username)
