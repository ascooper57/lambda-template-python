import json
import logging

import boto3
import psycopg2
import pytest
import requests
from boto3.session import Session

from api.rdb.config import get, is_test, is_production
from api.rdb.model import db_cursor, db_close, db_migrate
from api.rdb.utils.apigateway import get_api_url
from api.rdb.utils.cognito import get_cognito_username_id, get_cognito_user_pool_id
from api.rdb.utils.service_framework import STATUS_OK, STATUS_BAD_REQUEST
from .utilities import invoke, get_lambda_test_data, get_lambda_fullpath

cognito_idp_client = boto3.client('cognito-idp')
apigateway_client = boto3.client("apigateway")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DELETE_AFTER_CREATE = True

TESTER1 = "tester1@praktikos.com"
TESTER2 = "tester2@praktikos.com"

TESTERS = [TESTER1, TESTER2]

_ID_TOKEN = ""


def get_secure_event(lambda_function, aws=False):
    global _ID_TOKEN

    fullpath = get_lambda_fullpath(lambda_function)
    event = get_lambda_test_data(fullpath, authorization_token=_ID_TOKEN)
    if aws:
        # noinspection PyTypeChecker
        session = Session(region_name="us-east-1")
        credentials = session.get_credentials()
        event['body']['aws_access_key_id'] = credentials.access_key
        event['body']['aws_secret_access_key'] = credentials.secret_key
        sts_client = boto3.client("sts", aws_access_key_id=credentials.access_key,
                                  aws_secret_access_key=credentials.secret_key)
        aws_account_id = sts_client.get_caller_identity()["Account"]
        event['body']['aws_account_id'] = aws_account_id

    if 'body' in event and 'username' in event['body']:
        event['body']['username'] = get_cognito_username_id(cognito_idp_client,
                                                            TESTER1,
                                                            get_cognito_user_pool_id(cognito_idp_client,
                                                                                     cognito_user_pool_name="cognito71404f97_userpool_71404f97"))
    return event, fullpath


def really_delete_users():
    # Unconditionally Delete testers
    for tester in TESTERS:
        try:
            if is_test():
                fullpath = get_lambda_fullpath("LambdaApiUserSignUp")
                event = get_lambda_test_data(fullpath, authorization_token=_ID_TOKEN)
                # noinspection PyTypeChecker
                event['httpMethod'] = 'DELETE'
                username = get_cognito_username_id(cognito_idp_client,
                                                   tester,
                                                   event['body']['cognito_user_pool_id'])

                event['queryStringParameters'] = {
                    'cognito_user_pool_id': event['body']['cognito_user_pool_id'],
                    'force': True,
                    'username': username
                }
                event.pop('body', None)
                response2 = invoke(fullpath, event)
                assert response2  # "/user should return Status \"OK\"")
                assert response2['statusCode'] == STATUS_OK

            if is_production():
                fullpath = get_lambda_fullpath("LambdaApiUserSignUp")
                event = get_lambda_test_data(fullpath, authorization_token=_ID_TOKEN)
                event['httpMethod'] = 'DELETE'
                username = get_cognito_username_id(cognito_idp_client,
                                                   tester,
                                                   event['body']['cognito_user_pool_id'])

                event['queryStringParameters'] = {
                    'cognito_user_pool_id': event['body']['cognito_user_pool_id'],
                    'force': True,
                    'username': username
                }
                url = get_api_url(apigateway_client, 'API', '/v1', '/user/signup')
                # noinspection PyUnusedLocal
                response3 = requests.delete(url, params=event['queryStringParameters'])
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
            event['body']['email'] = tester
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
            event['body']['email'] = tester
            url = get_api_url(apigateway_client, 'API', '/v1', '/user/signup')
            response = requests.put(url, headers=event['headers'], data=json.dumps(event['body']))
            response_data = json.loads(response.text)
            if response.status_code == STATUS_BAD_REQUEST:
                assert response_data['Code'] == "UsernameExistsException"
                # noinspection PyUnusedLocal
                response = requests.get(url, params=event['body'])
            else:
                assert response.status_code == STATUS_OK


COGNITO_REGION = "COGNITO_REGION"
COGNITO_USER_POOL_ID = "COGNITO_USER_POOL_ID"


@pytest.fixture(scope="session")
def cognito_settings():
    cognito_user_pool_id = get_cognito_user_pool_id(cognito_idp_client,
                                                    cognito_user_pool_name="cognito71404f97_userpool_71404f97")
    return {
        "cognito.region": 'us-east-1',
        "cognito.userpool.id": cognito_user_pool_id
    }


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
    username = get_cognito_username_id(cognito_idp_client,
                                       event['body']['email'],
                                       event['body']['cognito_user_pool_id'])
    event['body']['username'] = username
    event['body'].pop('email', None)
    # Update user tester1@praktikos.com
    payload = {"httpMethod": "POST", "body": event['body']}
    response1 = invoke(fullpath, payload)
    assert len(response1['body'])
    response_data = json.loads(response1['body'])
    assert response1['statusCode'] == STATUS_OK
    assert response_data['Username']
    assert event['body']['username'] == response_data['Username']
    assert 'UserCreateDate' in response_data
    assert 'UserLastModifiedDate' in response_data
    assert 'Enabled' in response_data
    assert 'UserStatus' in response_data

    fullpath = get_lambda_fullpath("LambdaApiUserSignIn")
    event = get_lambda_test_data(fullpath)
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
    if is_test() and get('rdb.pg.database').endswith('test'):
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
    conn = psycopg2.connect(database=get('rdb.pg.database'))
    conn.set_isolation_level(0)

    try:
        _cursor = conn.cursor()
        _cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore ")
    finally:
        conn.close()


def _drop_database(cursor):
    if is_test() and get('rdb.pg.database').endswith('test'):
        try:
            # cursor.execute("SELECT * from pg_stat_activity;")
            # result = cursor.fetchall()
            cursor.execute("DROP DATABASE %s" % get('rdb.pg.database'))
        except Exception as ex:
            logger.error(str(ex))


def _create_database(cursor):
    if is_test() and get('rdb.pg.database').endswith('test'):
        try:
            cursor.execute("CREATE DATABASE %s ENCODING 'UTF8'" % get('rdb.pg.database'))

        except psycopg2.ProgrammingError as ex:
            logger.error(str(ex))
