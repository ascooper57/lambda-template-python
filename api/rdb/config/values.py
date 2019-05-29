# -*- coding: utf-8 -*-
import re

# noinspection PyProtectedMember
from .files import _home

_re_key = re.compile(r'[a-z][\w\-\.\$]{2,200}', re.I)
_re_env_append = re.compile(r'.*[-_]$')
_re_env_sub = re.compile(r'\{ENV\}')
_re_home = re.compile(r'^\~')


def valid_key(k):
    global _re_key
    return _re_key.match(k) is not None


def expand_value(v, environment):
    # append the name of the environment if a string value ends with '_'
    try:
        if isinstance(v, str):
            if _re_env_sub.search(v):
                v = _re_env_sub.sub(environment, v)
            elif _re_env_append.match(v):
                v = v + environment
    except AttributeError:
        pass
    try:
        if isinstance(v, str):
            v = _re_home.sub(_home(), v)
    except AttributeError:
        pass
    return v
