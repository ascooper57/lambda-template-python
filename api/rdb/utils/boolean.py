# -*- coding: utf-8 -*-

import re

re_boolean_true = re.compile(r'^(t|yes|on)', re.I)
re_boolean_false = re.compile(r'^(f|no|off)', re.I)


def as_bool(flag):
    """
    Return a flag as a boolean
    """
    global re_boolean_true, re_boolean_false

    if isinstance(flag, (int, float,)):
        return int(flag) > 0

    if re_boolean_true.match(flag):
        return True

    if re_boolean_false.match(flag):
        return False

    raise ValueError(flag)
