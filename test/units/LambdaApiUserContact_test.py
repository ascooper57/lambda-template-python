# -*- coding: utf-8 -*-

import boto3
import json
import requests

from api.rdb.config import is_test, is_production
from ..utilities import invoke
from api.rdb.utils.service_framework import STATUS_OK
from api.rdb.utils.apigateway import get_api_url
from ..conftest import get_secure_event


# noinspection PyUnusedLocal
def test(empty_database, create_and_delete_user, create_login_session, create_user_contact):
    pass
