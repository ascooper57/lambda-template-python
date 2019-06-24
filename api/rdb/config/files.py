# -*- coding: utf-8 -*-
import codecs
import json
import logging
import os
import re

logger = logging.getLogger(__name__)


def candidate_files(module, environment, prefix=None):
    """
    List of target files in increasing order of
    precedence.
    """
    return _uniq(_candidate_files(module, environment, prefix))


# noinspection PyUnusedLocal
def candidate_directories(module):
    """
    List of target directories in increasing order of
    precedence.
    """
    # the base relative to the file declaring the module
    module_base_path = os.path.dirname(module.__file__)
    # the config directory in that dir
    module_path = os.path.join(module_base_path, 'config')

    # the order is important - this detemines precedence (later is higher)
    return [
        module_path,
        _cwd_path()
    ]


def read_file(path):
    h = {}
    prefix = ''

    def _update(d):
        if d:
            for k, v in d.items():
                if k and v is not None:
                    h[prefix + k] = v

    try:
        if os.path.exists(path):
            # logger.debug("reading config from: %s" % path)
            with codecs.open(path, encoding="utf8") as fd:
                if path.endswith('.json'):
                    _update(json.load(fd))
    except FileNotFoundError:
        pass

    return h


def module_name(module):
    return module.__name__.split('.')[-1]


def _candidate_files(module, environment, prefix=None, pattern=None):
    home = _home()

    for d in candidate_directories(module):
        for f in _candidate_basenames(module, environment, d, prefix, pattern):
            dot = '.' if d == home else ''
            yield os.path.join(d, dot + f + '.json')


def _candidate_basenames(module, environment, dirname, prefix=None, pattern=None):
    if prefix:
        prefixes = [prefix]
    elif pattern:
        if not isinstance(pattern, type(re.compile('.'))):
            pattern = re.compile(pattern)
        try:
            def _matched(s):
                match = pattern.match(s)
                if match:
                    return match.group(0)

            prefixes = list(filter(None, (_matched(entry.name) for entry in os.scandir(dirname))))
        except (FileNotFoundError, NotADirectoryError):
            prefixes = []
    else:
        prefixes = [module_name(module)]
    return prefixes
    # for prefix in prefixes:
    #     for suffix in ('', '_' + environment, '-' + environment):
    #         yield prefix + suffix


def _home():
    return os.path.expanduser("~")


def _cwd_path():
    return os.path.join(os.getcwd(), 'config')


def _uniq(seq):
    # order preserving uniqueness
    # http://www.peterbe.com/plog/uniqifiers-benchmark
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]
