#!/usr/bin/env python

import logging
import sys

logger = logging.getLogger(__name__)


def migrate_database():
    from api.rdb.model.schema import db_migrate
    """Create and ensure proper schema"""
    logger.info("migrating database")
    db_migrate()


def config():
    # example: ./cli.py config LambdaApiTemplateJS region
    if len(sys.argv) > 2:
        import json
        import os
        import boto3
        lambda_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "lambda_functions", sys.argv[2]))
        filename = "%s/config.json" % lambda_directory
        with open(filename, 'r') as fd:
            contents = json.load(fd)
            contents.update({'account_id': boto3.client("sts").get_caller_identity()["Account"]})
            val = contents[sys.argv[3]]
            # print(val)
            return val


if __name__ == '__main__':
    """
    administration
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == "migrate":
            migrate_database()
        elif sys.argv[1] == "config":
            sys.exit(config())
        else:
            raise Exception("Unrecognized command: %s" % sys.argv[1])
