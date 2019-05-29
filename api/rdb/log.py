# -*- coding: utf-8 -*-

import logging
import logging.config
import sys

from .config import get

"""
Create a log handler based on certain configuration paramaters.
"""
_stdout_handler = logging.StreamHandler(sys.stdout)


def build_logger(verbose=False):
    for _name in ("rdb", "peewee",):
        log = logging.getLogger(_name)
        log.setLevel(get('rdb.log.level'))
        if verbose:
            log.addHandler(_stdout_handler)
            log.setLevel(logging.DEBUG)
