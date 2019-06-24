# -*- coding: utf-8 -*-

# list of all valid environments
_environments = ('test', 'staging', 'production')


def environments():
    """
    Returns the list of all known environments.
    """
    return _environments
