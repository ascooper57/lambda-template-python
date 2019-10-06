# -*- coding: utf-8 -*-
import datetime
import json
import time
from os import getcwd

import boto3

from api.rdb.config import get
from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


#              ,-------.
#              |/backup|
#              `-------'
#
#
# ,---------------.  ,---------------.
# |GET /backup    |  |OPTIONS /backup|
# |---------------|  |---------------|
# |.. responses ..|  |.. responses ..|
# |200: Empty     |  |200: Empty     |
# |---------------|  |---------------|
# `---------------'  `---------------'
#
#               ,-----.
#               |Empty|
#               `-----'


# noinspection PyUnusedLocal
def handler(request, context):
    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> dict
        logger.debug('entered:' + context.function_name)
        current_time = datetime.datetime.now()
        current_date = str(current_time.strftime("%Y-%m-%d"))
        name = context.function_name
        logger.info("Your backup" + name + " ran at " + str(current_time))
        s3_resource = boto3.resource('s3', region_name=get('aws_cognito_region'))
        logger.info("Got s3 client")
        sts_client = boto3.client("sts", region_name=get('aws_cognito_region'))
        logger.info("Got sts client")
        aws_account_id = sts_client.get_caller_identity()["Account"]
        duration = 0
        duration += backup_cognito(s3_resource, aws_account_id, current_date)
        logger.info("duration= %d" % duration)
        duration += backup_iam(s3_resource, aws_account_id, current_date)
        logger.info("duration= %d" % duration)
        duration += backup_api_gateway(s3_resource, aws_account_id, current_date)
        logger.info("duration= %d" % duration)
        duration += backup_cloudfront(s3_resource, aws_account_id, current_date)
        logger.info("duration= %d" % duration)
        duration += backup_route53(s3_resource, aws_account_id, current_date)
        logger.info("duration= %d" % duration)
        return {"duration": duration}

    return handle_request(request, context, http_get=http_get)


def backup_api_gateway(s3_resource, aws_account_id, current_date):
    # type: ('boto3.client("s3")', str, str) -> float
    logger.info("backup apigateway ran at " + str(datetime.datetime.now()))
    t0 = time.time()
    bucket_name = "backup-apigateway-%s" % aws_account_id
    s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
    s3_bucket = s3_resource.Bucket(bucket_name)
    # http://boto3.readthedocs.io/en/latest/reference/services/apigateway.html#APIGateway.Client.get_export
    api_gateway_client = boto3.client('apigateway', region_name=get('aws_cognito_region'))
    apis = api_gateway_client.get_rest_apis(limit=500)
    for api in apis['items']:
        stages = api_gateway_client.get_stages(restApiId=api['id'])
        for stage in stages['item']:
            api_gateway_dict = api_gateway_client.get_export(restApiId=api['id'], stageName=stage['stageName'],
                                                             exportType='swagger',
                                                             parameters={'extensions': 'integrations'},
                                                             accepts='application/json')
            # Upload the file to S3
            key = current_date + '-' + api['name'] + '-' + stage['stageName'] + '-backup.json'
            s3_bucket.put_object(Key=key, Body=api_gateway_dict['body'].read())
    t1 = time.time()
    return t1 - t0


def backup_cloudfront(s3_resource, aws_account_id, current_date):
    # type: ('boto3.client("s3")', str, str) -> float
    logger.info("backup cloudfront ran at " + str(datetime.datetime.now()))
    t0 = time.time()
    bucket_name = "backup-cloudfront-%s" % aws_account_id
    s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
    s3_bucket = s3_resource.Bucket(bucket_name)
    cloudfront_client = boto3.client('cloudfront', region_name=get('aws_cognito_region'))
    distributions = cloudfront_client.list_distributions()
    if 'Items' in distributions['DistributionList']:
        for item in distributions['DistributionList']['Items']:
            cloudfront_config = cloudfront_client.get_distribution_config(Id=item['Id'])
            b = bytearray()
            b.extend(map(ord, json.dumps(cloudfront_config, indent=4)))
            # Upload the file to S3
            key = current_date + '-' + item['Id'] + '-backup.json'
            s3_bucket.put_object(Key=key, Body=b)
    t1 = time.time()
    return t1 - t0


def backup_route53(s3_resource, aws_account_id, current_date):
    # type: ('boto3.client("s3")', str, str) -> float
    logger.info("backup route53 ran at " + str(datetime.datetime.now()))
    t0 = time.time()
    bucket_name = "backup-route53-%s" % aws_account_id
    s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
    s3_bucket = s3_resource.Bucket(bucket_name)
    route53_client = boto3.client('route53')
    hosted_zones = route53_client.list_hosted_zones()
    for hosted_zone in hosted_zones['HostedZones']:
        tokens = hosted_zone['Id'].split('/')
        route53_records = route53_client.list_resource_record_sets(HostedZoneId=tokens[2])
        b = bytearray()
        b.extend(map(ord, json.dumps(route53_records, indent=4)))
        # Upload the file to S3
        key = current_date + '-' + hosted_zone['Name'] + '-backup.json'
        s3_bucket.put_object(Key=key, Body=b)
    t1 = time.time()
    return t1 - t0


def backup_iam(s3_resource, aws_account_id, current_date):
    # type: ('boto3.client("s3")', str, str) -> float
    logger.info("backup iam ran at " + str(datetime.datetime.now()))
    t0 = time.time()
    bucket_name = "backup-iam-%s" % aws_account_id
    s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
    s3_bucket = s3_resource.Bucket(bucket_name)
    iam_client = boto3.client('iam')
    user_dict = {}
    groups = []
    for userlist in iam_client.list_users()['Users']:
        user_groups = iam_client.list_groups_for_user(UserName=userlist['UserName'])
        print("Username: " + userlist['UserName'])
        print("Assigned groups: ")
        groups = []
        for group_name in user_groups['Groups']:
            print(group_name)
            groups += [group_name['GroupName']]
            user_dict[userlist['UserName']] = json.dumps(groups)
    b = bytearray()
    b.extend(map(ord, json.dumps(user_dict, indent=4)))
    # Upload the file to S3
    s3_bucket.put_object(Key=current_date + '-users-backup.json', Body=b)

    policies = []
    for group in groups:
        policies.append({group: iam_client.list_attached_group_policies(
            GroupName=group,
            MaxItems=500
        )})
    s3_bucket.put_object(Key=current_date + '-group-policies-backup.json', Body=json.dumps(policies, indent=4))

    role_names = [
        "cognito71404f97_sns-role",
        "cognito71404f97_userpoolclient_lambda_role"
    ]

    roles = []
    for role_name in role_names:
        roles.append({role_name: iam_client.list_attached_role_policies(RoleName=role_name)})
    s3_bucket.put_object(Key=current_date + '-roles-backup.json', Body=json.dumps(roles, indent=4))
    t1 = time.time()
    return t1 - t0


def backup_cognito(s3_resource, aws_account_id, current_date):
    # type: ('boto3.client("s3")', str, str) -> float
    logger.info("backup cognito ran at " + str(datetime.datetime.now()))
    t0 = time.time()
    bucket_name = "backup-cognito-%s" % aws_account_id
    s3_resource.create_bucket(ACL='private', Bucket=bucket_name)
    s3_bucket = s3_resource.Bucket(bucket_name)
    cognito_idp_client = boto3.client('cognito-idp')
    user_pools = cognito_idp_client.list_user_pools(
        MaxResults=60
    )
    user_pool_list = []
    user_pool_client_list = []
    identity_pool_list = []
    for user_pool in user_pools['UserPools']:
        response = cognito_idp_client.describe_user_pool(UserPoolId=user_pool['Id'])
        response['UserPool']['LastModifiedDate'] = None
        response['UserPool']['CreationDate'] = None
        user_pool_list.append(response['UserPool'])

        user_pool_clients = cognito_idp_client.list_user_pool_clients(
            UserPoolId=response['UserPool']['Id'],
            MaxResults=60
        )

        for user_pool_client in user_pool_clients['UserPoolClients']:
            response = cognito_idp_client.describe_user_pool_client(UserPoolId=user_pool_client['UserPoolId'],
                                                                    ClientId=user_pool_client['ClientId'])
            response['UserPoolClient']['LastModifiedDate'] = None
            response['UserPoolClient']['CreationDate'] = None
            user_pool_client_list.append(response['UserPoolClient'])

    cognito_identity_client = boto3.client('cognito-identity')
    identity_pools = cognito_identity_client.list_identity_pools(MaxResults=60)
    for idenity_pool in identity_pools['IdentityPools']:
        response = cognito_identity_client.describe_identity_pool(IdentityPoolId=idenity_pool['IdentityPoolId'])
        response.pop('ResponseMetadata', None)
        identity_pool_list.append(response)

    # save cognito user pool configuration
    b = bytearray()
    b.extend(map(ord, json.dumps(user_pool_list, indent=4)))
    # Upload the file to S3
    s3_bucket.put_object(Key=current_date + '-user_pool-backup.json', Body=b)

    # save cognito user pool client configuration
    b = bytearray()
    b.extend(map(ord, json.dumps(user_pool_client_list, indent=4)))
    # Upload the file to S3
    s3_bucket.put_object(Key=current_date + '-user_pool_app_client-backup.json', Body=b)

    # save cognito (Federated) idenity pool configuration
    b = bytearray()
    b.extend(map(ord, json.dumps(identity_pool_list, indent=4)))
    # Upload the file to S3
    s3_bucket.put_object(Key=current_date + '-identity_pool-backup.json', Body=b)
    t1 = time.time()
    return t1 - t0
