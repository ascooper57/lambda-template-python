# -*- coding: utf-8 -*-

from os import getcwd

from api.rdb.utils.lambda_logger import lambda_logger
from api.rdb.utils.service_framework import handle_request

logger = lambda_logger(__name__, getcwd())


# This is the lambda handler - it calls a general purpose service framework that
# deals with all the http cruft
# request is the http request that is passed in by API gateway proxy
# implement the http verb responses as needed
# delete the rest and the arguments to handle_request
def handler(request, context):
    from api.rdb.model.sample import Sample

    # noinspection PyPep8Naming, PyUnusedLocal
    def http_get(request_params, request_body):
        # type: (dict, dict) -> list
        # Note request_params, request_body can have values of None
        logger.info("http_get")
        index_key_example = request_params['index_key_example']
        samples = []
        for sample in Sample.select().where(Sample.index_key_example == index_key_example):
            samples += [sample.__data__]
        return samples

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_put(request_params, request_body):
        # type: (dict, dict) -> dict
        # Note request_params, request_body can have values of None
        logger.info("http_put")
        with Sample.atomic():
            sample = Sample.create(**request_body)
            # noinspection PyProtectedMember
            return sample.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_post(request_params, request_body):
        # type: (dict, dict) -> dict
        # Note request_params, request_body can have values of None
        logger.info("http_post")
        # noinspection PyShadowingBuiltins
        id = request_body['id']
        # noinspection PyUnresolvedReferences
        sample = Sample.get(Sample.id == id)

        if "index_key_example" in request_body:
            sample.index_key_example = request_body["index_key_example"]
        if "integer_example" in request_body:
            sample.integer_example = request_body["integer_example"]
        if "datetime_example" in request_body:
            sample.datetime_example = request_body["datetime_example"]
        if "text_example" in request_body:
            sample.text_example = request_body["text_example"]
        if "decimal_example" in request_body:
            sample.decimal_example = request_body["decimal_example"]
        if "boolean_example" in request_body:
            sample.boolean_example = request_body["boolean_example"]
        # save updated fields
        with sample.atomic():
            sample.save()
        return sample.__data__

    # noinspection PyPep8Naming,PyUnusedLocal
    def http_delete(request_params, request_body):
        # type: (dict, dict) -> dict
        # Note request_params, request_body can have values of None
        logger.info("http_delete")
        with Sample.atomic():
            # noinspection PyUnresolvedReferences
            Sample.delete().where(Sample.id == request_params["id"]).execute()
        return {}

    # noinspection PyPep8

    return handle_request(request, context, http_get=http_get, http_put=http_put, http_post=http_post,
                          http_delete=http_delete)
