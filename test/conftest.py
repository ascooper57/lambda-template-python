import json
import logging

import boto3
import psycopg2
import pytest
import requests
from boto3.session import Session

from api.rdb.config import get, is_test, is_production
from api.rdb.model import db_cursor, db_close, db_migrate
from api.rdb.model.table_user_profile import User_profile
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.service_framework import STATUS_OK, STATUS_BAD_REQUEST, STATUS_FORBIDDEN
from .utilities import invoke, get_lambda_test_data, get_lambda_fullpath

cognito_idp_client = boto3.client('cognito-idp')
apigateway_client = boto3.client("apigateway")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DELETE_AFTER_CREATE = True

TESTER1 = "TESTER1"
TESTER2 = "TESTER2"

TESTERS = [TESTER1, TESTER2]

_ID_TOKEN = ""


def get_secure_event(lambda_function, aws=False):
    global _ID_TOKEN

    fullpath = get_lambda_fullpath(lambda_function)
    event = get_lambda_test_data(fullpath, authorization_token=_ID_TOKEN)
    param = 'body' if 'body' in event else 'queryStringParameters'
    if aws:
        # noinspection PyTypeChecker
        session = Session(region_name=get('aws_region_name'))
        credentials = session.get_credentials()
        event[param]['aws_access_key_id'] = credentials.access_key
        event[param]['aws_secret_access_key'] = credentials.secret_key
        sts_client = boto3.client("sts", aws_access_key_id=credentials.access_key,
                                  aws_secret_access_key=credentials.secret_key)
        aws_account_id = sts_client.get_caller_identity()["Account"]
        event[param]['aws_account_id'] = aws_account_id

    if 'username' in event[param]:
        event[param]['username'] = TESTER1
    if 'recipient_username' in event[param]:
        event[param]['recipient_username'] = TESTER1
    if 'blocked_username' in event[param]:
        event[param]['blocked_username'] = TESTER2
    if 'from_username' in event[param]:
        event[param]['from_username'] = TESTER2
    if param in event and 'to_username' in event[param]:
        event[param]['to_username'] = TESTER1
    return event, fullpath


def really_delete_users():
    # Unconditionally Delete testers
    for tester in TESTERS:
        # noinspection PyBroadException,PyUnusedLocal
        try:
            event, fullpath = get_secure_event("LambdaApiUserContact")
            event['body']['username'] = tester
            payload = {"httpMethod": "GET", "queryStringParameters": event['body']}
            response2 = invoke(fullpath, payload)
            if response2['statusCode'] == STATUS_OK:
                response_data = json.loads(response2['body'])
                assert 'TopicArn' in response_data
                assert response_data['TopicArn'].startswith("arn:aws:sns:")
                # noinspection PyShadowingBuiltins
                payload = {"httpMethod": "DELETE", "queryStringParameters": {"topic_arn": response_data['TopicArn']}}
                # noinspection PyTypeChecker
                response3 = invoke(fullpath, payload)
                assert response3['statusCode'] == STATUS_OK
        except Exception as ex:
            pass

        try:
            fullpath = get_lambda_fullpath("LambdaApiUserSignUp")
            event = get_lambda_test_data(fullpath, authorization_token=_ID_TOKEN)
            # noinspection PyTypeChecker
            event['httpMethod'] = 'DELETE'
            event['queryStringParameters'] = {
                'force': True,
                'username': tester
            }
            event.pop('body', None)
            if is_test():
                response2 = invoke(fullpath, event)
                assert response2  # "/user should return Status \"OK\"")
                assert response2.status_code == STATUS_OK
            elif is_production():
                url = get_api_url(apigateway_client, 'API', '/v1', '/user/signup')
                # noinspection PyUnusedLocal
                response3 = requests.delete(url, params=event['queryStringParameters'])
                assert response3.status_code != STATUS_FORBIDDEN

        # except cognito_idp_client.exceptions.UserNotFoundException as ex:
        except Exception as ex:
            logger.info(str(ex))


# noinspection PyUnusedLocal
@pytest.fixture(scope='function')
def delete_users():
    really_delete_users()


# noinspection PyProtectedMember
@pytest.fixture(scope='function')
def create_users(delete_users):
    # Create testers
    for tester in TESTERS:
        if is_test():
            fullpath = get_lambda_fullpath("LambdaApiUserSignUp")
            event = get_lambda_test_data(fullpath)
            event['body']['username'] = tester
            response = invoke(fullpath, event)
            assert response['body']
            body = json.loads(response['body'])
            if response['statusCode'] == STATUS_BAD_REQUEST:
                assert body['Code'] == "UsernameExistsException"
                payload = {"httpMethod": "GET", "queryStringParameters": event['body']}
                # noinspection PyTypeChecker,PyUnusedLocal
                response = invoke(fullpath, payload)
            else:
                assert response['statusCode'] == STATUS_OK
                assert body['Username']

        if is_production():
            # noinspection PyBroadException,PyUnusedLocal
            event = get_lambda_test_data(get_lambda_fullpath("LambdaApiUserSignUp"))
            event['body']['username'] = tester
            event['body'].pop('newpassword', None)
            url = get_api_url(apigateway_client, 'API', '/v1', '/user/signup')
            response = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
            response_data = json.loads(response.text)
            if response.status_code == STATUS_BAD_REQUEST:
                assert response_data['Code'] == "UsernameExistsException"
                # noinspection PyUnusedLocal
                response = requests.get(url, params=event['body'])
            else:
                assert response.status_code == STATUS_OK

        # update database
        session = Session(region_name=get('aws_region_name'))

        data = {
            "username": tester,
            "avatar": "00000000-0000-0000-0000-000000000000"
        }
        # noinspection PyBroadException,PyUnusedLocal
        with User_profile.atomic():
            query = User_profile.update(**data).where(User_profile.username == tester)
            count = query.execute()
            assert count == 1


# noinspection PyTypeChecker, noinspection PyBroadException
@pytest.fixture(scope='function')
def create_and_delete_user(create_users):
    # NEW CODE GEN HERE

    yield create_and_delete_user

    if DELETE_AFTER_CREATE:
        really_delete_users()


# noinspection PyTypeChecker, noinspection PyBroadException
@pytest.fixture(scope='function')
def create_login_session():
    global _ID_TOKEN

    # new user, FORCE_CHANGE_PASSWORD required
    event, fullpath = get_secure_event("LambdaApiUserSignUp")
    # Update user tester1@praktikos.com
    payload = {"httpMethod": "POST", "body": event['body']}
    response1 = invoke(fullpath, payload)
    assert response1['statusCode'] == STATUS_OK
    assert len(response1['body'])
    response_data = json.loads(response1['body'])
    assert response_data['Username']
    assert event['body']['username'] == response_data['Username']
    assert 'UserCreateDate' in response_data
    assert 'UserLastModifiedDate' in response_data
    assert 'Enabled' in response_data
    assert 'UserStatus' in response_data

    fullpath = get_lambda_fullpath("LambdaApiUserSignIn")
    event = get_lambda_test_data(fullpath)
    # event['body']['username'] = username
    # event['body'].pop('email', None)
    # https://github.com/nficano/python-lambda
    # noinspection PyTypeChecker
    response1 = invoke(fullpath, event)
    assert response1 is not None  # "/user/signin should return Status \"OK\"")
    assert response1["statusCode"] == STATUS_OK
    assert "body" in response1
    body = response1['body']
    response_data = json.loads(body)
    assert "user" in response_data
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert "id_token" in response_data
    assert "token_type" in response_data
    assert "expires_in" in response_data
    assert response_data["token_type"] == "Bearer"
    assert response_data["expires_in"] == 3600
    _ID_TOKEN = response_data['id_token']


# noinspection PyTypeChecker, noinspection PyBroadException
@pytest.fixture(scope='function')
def create_user_contact():
    event, fullpath = get_secure_event("LambdaApiUserContact")
    payload = {"httpMethod": "PUT", "body": event['body']}
    response1 = invoke(fullpath, payload)
    assert response1['statusCode'] == STATUS_OK
    body = response1['body']
    assert body
    data = json.loads(response1['body'])
    assert data
    assert 'topic_arn' in data
    assert data['topic_arn'].startswith('arn:aws:sns')

    if is_test():
        payload = {"httpMethod": "GET", "queryStringParameters": event['body']}
        response2 = invoke(fullpath, payload)
        assert response2['statusCode'] == STATUS_OK
        response_data = json.loads(response2['body'])
        assert 'TopicArn' in response_data
        assert response_data['TopicArn'].startswith("arn:aws:sns:")
    elif is_production():
        # event, fullpath = get_secure_event("LambdaApiUserProfile")
        # url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/profile')
        # response = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
        # assert response.status_code == STATUS_OK
        # event, fullpath = get_secure_event("LambdaApiUserContact")
        url = get_api_url(boto3.client("apigateway"), 'API', '/v1', '/user/contact')
        response4 = requests.get(url, headers=event['headers'], params=event['body'])
        assert response4.status_code == STATUS_OK
        response_data = json.loads(response4.text)
        # assert any(event['username'] in s['username'] for s in data)

@pytest.fixture
def fixture_directory():
    import os
    return os.path.join(os.path.dirname(__file__), "fixtures")


# ### Relational Database functions ###

def close():
    db_close()


# noinspection PyUnusedLocal,PyShadowingNames
@pytest.fixture(scope='function')
def empty_database(request, raw_database):
    db_migrate()
    # called when
    request.addfinalizer(close)
    return db_cursor


@pytest.fixture(scope='function')
def raw_database():
    if is_test() and get('database').endswith('test'):
        conn = psycopg2.connect(database='postgres')
        conn.set_isolation_level(0)

        # noinspection PyUnusedLocal
        try:
            _cursor = conn.cursor()
            _drop_database(_cursor)
            _create_database(_cursor)
        except psycopg2.OperationalError as ex:
            pass
        finally:
            conn.close()

        _create_extensions()
    return db_cursor


def _create_extensions():
    conn = psycopg2.connect(database=get('database'))
    conn.set_isolation_level(0)

    try:
        _cursor = conn.cursor()
        _cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore ")
    finally:
        conn.close()


def _drop_database(cursor):
    if is_test() and get('database').endswith('test'):
        try:
            # cursor.execute("SELECT * from pg_stat_activity;")
            # result = cursor.fetchall()
            cursor.execute("DROP DATABASE %s" % get('database'))
        except Exception as ex:
            logger.error(str(ex))


def _create_database(cursor):
    if is_test() and get('database').endswith('test'):
        try:
            cursor.execute("CREATE DATABASE %s ENCODING 'UTF8'" % get('database'))

        except psycopg2.ProgrammingError as ex:
            logger.error(str(ex))
