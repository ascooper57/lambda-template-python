# -*- coding: utf-8 -*-
import json
import logging
import os

from .json_serializer import json_serialize

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cwd = os.getcwd()
logger.info(cwd)
logger.info(str(os.listdir(path=".")))

# https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
STATUS_OK = 200  # OK
STATUS_OK_NO_CONTENT = 204  # NO CONTENT
STATUS_BAD_REQUEST = 400  # BAD REQUEST
STATUS_UNAUTHORIZED = 401  # BAD REQUEST
STATUS_FORBIDDEN = 403  # The server understood the request but refuses to authorize it
STATUS_NOT_FOUND = 404  # Not FOUND


def get_request_body(request):
    if 'body' in request and isinstance(request['body'], str):
        request_body = json.loads(request['body'])
    else:
        request_body = request['body'] if 'body' in request else None
    return request_body


def get_request_params(request):
    if 'queryStringParameters' in request and isinstance(request['queryStringParameters'], str):
        request_params = json.loads(request['queryStringParameters'])
    else:
        request_params = request['queryStringParameters'] if 'queryStringParameters' in request else None
    return request_params


def get_api_gateway_request(request):
    try:
        if 'path' in request and 'headers' in request:
            url = "%s://%s%s" % (request['headers']['X-Forwarded-Proto'], request['headers']['Host'], request['path'])
            if request['httpMethod'] == 'GET':
                return 'curl %s' % url
            else:
                request_body = get_request_body(request)
                payload = '-d \'%s\'' % request_body if request_body else ''
                return 'curl -H "Content-Type: application/json" -X %s %s %s' % (request['httpMethod'], payload, url)
    except Exception as ex:
        logger.warning(str(ex))


# event – AWS Lambda uses this parameter to pass in event data to the handler.
# This parameter is usually of the Python dict type.
# It can also be list, str, int, float, or NoneType type.
# Example: message = 'Hello {} {}!'.format(event['first_name'], event['last_name'])
# noinspection PyUnusedLocal
def handle_request(request, context, http_get=None, http_put=None, http_delete=None, http_post=None):
    logger.debug('entered:' + context.function_name)
    from peewee import DoesNotExist
    # logger.debug(get('rdb.pg.database'))
    logger.info(get_api_gateway_request(request))

    status_code = STATUS_OK
    body = {}
    try:
        request_params = get_request_params(request)
        request_body = get_request_body(request)

        logger.info("REQUEST: %s" % request)
        logger.info("REQUEST BODY: " + json.dumps(request_body))
        logger.info("REQUEST PARAMS: " + json.dumps(request_params))

        if request['httpMethod'] == 'PUT':
            result = http_put(request_params, request_body)

        elif request['httpMethod'] == 'POST':
            result = http_post(request_params, request_body)

        elif request['httpMethod'] in 'DELETE':
            result = http_delete(request_params, request_body)

        elif request['httpMethod'] in 'GET':
            result = http_get(request_params, request_body)
        else:
            raise Exception('request http method must be [DELETE, GET, POST, PUT], received %s' % request['httpMethod'])

        # result is either a dict containing the body or a tuple of form(staus_code, error_string)
        if isinstance(result, tuple):
            status_code = result[0]
            body = result[1]
        else:
            body = result

    except DoesNotExist as ex:
        status_code = STATUS_NOT_FOUND
        body = ex.response['Error'] if hasattr(ex, 'response') else {"Message": str(ex)}
    except KeyError as ex:
        status_code = STATUS_BAD_REQUEST
        body = {"Message": "Param %s is not valid" % json.dumps(ex.args)}
    except Exception as ex:
        status_code = STATUS_BAD_REQUEST
        body = ex.response['Error'] if hasattr(ex, 'response') else {"Message": str(ex)}

    #
    # http://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
    # With Lambda, AWS or HTTP integrations, you can leverage API Gateway to set up the required headers using the
    # method response and integration response. For Lambda or HTTP proxy integrations, you can still set up the
    # required OPTIONS response headers in API Gateway. However, you must rely on the back end to return the
    # Access-Control-Allow-Origin headers because the integration response is disabled for the proxy integration.
    #
    if not body:
        body = '{}'
    elif not isinstance(body, str):
        json_serialize(body)
        logger.info(str(body))
        body = json.dumps(body)
    retval = {"isBase64Encoded": False,
              "statusCode": status_code,
              "headers": {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Headers':
                      'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Api-Header',
                  'Access-Control-Allow-Credentials': True,
                  'Content-Type': 'application/json'
              },
              "body": body
              }
    if status_code != STATUS_OK:
        logger.error(str(retval))
    return retval

    # "headers": {"Content-Type": "application/json",
    #             "X-Requested-With": "*",
    #             "Access-Control-Allow-Origin": "*",
    #             "Access-Control-Allow-Methods": "POST,GET,PUT,OPTIONS",
    #             "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with"
    #             },  # "$ref": "https://apigateway.amazonaws.com/restapis/syzd78/models/MediaQueryResponse"
