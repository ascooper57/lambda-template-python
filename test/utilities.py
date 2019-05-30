# -*- coding: utf-8 -*-

import json
import os
import sys
import time


class Context:
    def __init__(self, function_name):
        self.function_name = function_name


def invoke(src, event, verbose=False):
    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.json and handler module (e.g.: lambda_function.py).
    :param dict event:
        Specify which event json input file to use.
    :param bool verbose:
        Whether to print out verbose details.
    """
    # Load and parse the config file.
    cfg = get_config(src)

    # Load environment variables from the config file into the actual
    # environment.
    for key, value in cfg.get('environment_variables').items():
        os.environ[key] = value

    # Load and parse event file.
    # event = get_lambda_test_data(src, alt_event)

    # Tweak to allow module to import local modules
    # noinspection PyBroadException,PyUnusedLocal
    try:
        sys.path.index(src)
    except Exception as ex:
        sys.path.append(src)

    handler = cfg.get('handler')
    # Inspect the handler string (<module>.<function name>) and translate it
    # into a function we can execute.
    fn = get_callable_handler_function(src, handler)

    # TODO: look into mocking the ``context`` variable, currently being passed
    # as None.

    start = time.time()
    context = Context(cfg.get('function_name'))
    results = fn(event, context)
    end = time.time()

    print('{0}'.format(results))
    if verbose:
        print('\nexecution time: {:.8f}s\nfunction execution '
              'timeout: {:2}s'.format(end - start, cfg.get('timeout', 15)))
    return results


def get_callable_handler_function(src, handler):
    """Translate a string of the form "module.function" into a callable
    function.

    :param str src:
      The path to your Lambda project containing a valid handler file.
    :param str handler:
      A dot delimited string representing the `<module>.<function name>`.
    """
    from imp import load_source

    # "cd" into `src` directory.
    os.chdir(src)

    module_name, function_name = handler.split('.')
    filename = get_handler_filename(handler)

    path_to_module_file = os.path.join(src, filename)
    # importlib.find_loader(module_name, path_to_module_file)
    source_module = load_source(module_name, path_to_module_file)
    return getattr(source_module, function_name)


def get_handler_filename(handler):
    """Shortcut to get the filename from the handler string.

    :param str handler:
      A dot delimited string representing the `<module>.<function name>`.
    """
    module_name, _ = handler.split('.')
    return '{0}.py'.format(module_name)


def get_config(src):
    # type: (str) -> dict

    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.json and handler module (e.g.: lambda_function.py).
    """
    # Load and parse the config file.
    import os.path
    # https://codebeautify.org/yaml-to-json-xml-csv
    path_to_config_file = os.path.join(src, 'config.json')
    with open(path_to_config_file) as json_file:
        return json.load(json_file)


def get_lambda_test_data(src, authorization_token=None, alt_event_filename=None):
    # type: (str, str, str) -> dict

    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.json and handler module (e.g.: lambda_function.py).
    :param str authorization_token:
        An optional argument to add Cognito authorization id_token to event header.
    :param str alt_event_filename:
        An optional argument to override which event file to use.
    """

    # Load and parse event file.
    event_filename = alt_event_filename if alt_event_filename else 'event.json'
    path_to_event_file = os.path.join(src, event_filename)
    with open(path_to_event_file) as json_file:
        event = json.load(json_file)
        if 'headers' not in event:
            event['headers'] = dict(Authorization=authorization_token if authorization_token else '')
        elif authorization_token:
            event['headers']['Authorization'] = authorization_token
        return event


def get_lambda_fullpath(lambda_function):
    from os import path
    lambda_directory = path.abspath(
        path.join(path.dirname(__file__), ".." + os.path.sep + "api" + os.path.sep + "lambda_functions"))
    return path.realpath(path.join(lambda_directory, lambda_function))
