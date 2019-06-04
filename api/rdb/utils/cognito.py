# -*- coding: utf-8 -*-


def get_cognito_username_id(cognito_idp_client, email, cognito_user_pool_id):
    # type: ('boto3.client("cognito-idp")', str, str) -> str
    response = cognito_idp_client.list_users(
        UserPoolId=cognito_user_pool_id,
        Limit=1,
        Filter='email = "%s"' % email
    )
    if 'Users' in response and len(response['Users']):
        return response['Users'][0]['Username']

    # raise cognito_idp_client.exceptions.UserNotFoundException("User does not exist.")
    raise Exception("User does not exist.")


def get_cognito_user_pool_id(cognito_idp_client, cognito_user_pool_name):
    # type: ('boto3.client("cognito-idp")', str) -> str
    response = cognito_idp_client.list_user_pools(
        MaxResults=60
    )
    for user_pool in response['UserPools']:
        if user_pool['Name'] == cognito_user_pool_name:
            return user_pool['Id']
    raise Exception("Cognito User Pool %s not found" % cognito_user_pool_name)


def get_cognito_app_client_id(cognito_idp_client, cognito_user_pool_id):
    # type: ('boto3.client("cognito-idp")', str) -> str
    user_pool_clients = cognito_idp_client.list_user_pool_clients(
        UserPoolId=cognito_user_pool_id,
        MaxResults=60
    )
    # TODO: return app client that does not require app client secret
    for user_pool_client in user_pool_clients['UserPoolClients']:
        response = cognito_idp_client.describe_user_pool_client(
            UserPoolId=cognito_user_pool_id,
            ClientId=user_pool_client['ClientId']
        )
        if 'ClientSecret' not in response['UserPoolClient']:
            return user_pool_client['ClientId']
    raise Exception("Unable to find any Cognito User Pool app clients that doesn't require app client secret")


def validate_uuid4(uuid_string):
    # type: (str) -> None
    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """
    from uuid import UUID

    # If it's a value error exception, then the string is not a valid hex code for a UUID.
    val = UUID(uuid_string, version=4)

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.

    if val.hex == uuid_string.replace('-', ''):
        return
    raise ValueError("hexidecimal value in uuid do not match")
