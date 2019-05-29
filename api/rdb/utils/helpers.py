# -*- coding: utf-8 -*-
import json
import os
import sys
import time

from api.rdb.utils.lambda_logger import lambda_logger

logger = lambda_logger(__name__, os.getcwd())


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


def read(path, loader=None, binary_file=False):
    open_mode = 'rb' if binary_file else 'r'
    with open(path, mode=open_mode) as fh:
        if not loader:
            return fh.read()
        return loader(fh.read())


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
    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.json and handler module (e.g.: lambda_function.py).
    """
    # Load and parse the config file.
    import os.path
    # https://codebeautify.org/yaml-to-json-xml-csv
    path_to_config_file = os.path.join(src, 'config.json')
    cfg = read(path_to_config_file, loader=json.loads)
    return cfg


def get_lambda_test_data(src, authorization_token=None, alt_event=None):
    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.json and handler module (e.g.: lambda_function.py).
    :param str alt_event:
        An optional argument to override which event file to use.
    :param str authorization_token:
        An optional argument to add Cognito authorization id_token to event header.
    """

    # Load and parse event file.
    if alt_event:
        event = alt_event
    else:
        path_to_event_file = os.path.join(src, 'event.json')
        event = read(path_to_event_file, loader=json.loads)
        if 'headers' not in event:
            event['headers'] = dict(Authorization=authorization_token if authorization_token else '')
        elif authorization_token:
            event['headers']['Authorization'] = authorization_token
    return event


def zipdir(folder_path, ziph, exclude=None):
    if exclude is None:
        exclude = ['.DS_Store']
    from os import path, getcwd, chdir, walk

    current_working_directory = getcwd()
    chdir(folder_path)
    # ziph is zipfile handle
    toplevel = "."
    for root, dirs, files in walk(toplevel):
        for file in files:
            if not file in exclude:
                ziph.write(path.join(root, file))
    chdir(current_working_directory)


def imzipdir(folder_path, imzip):
    from os import path, getcwd, chdir, walk

    current_working_directory = getcwd()
    chdir(folder_path)
    # imzip is zipfile handle
    toplevel = "."
    for root, dirs, files in walk(toplevel):
        for file in files:
            file_path = path.join(root, file)
            print(file_path)
            imzip.append(file_path, get_file_binary_contents(file_path))

    chdir(current_working_directory)


# noinspection PyMethodMayBeStatic
def copy_directory(src, dest):
    import shutil

    try:
        shutil.copytree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)


# noinspection PyMethodMayBeStatic
def get_file_contents(filename, mode="r"):
    with open(filename, mode) as f:
        contents = f.read()
        f.close()
        return contents


def get_file_binary_contents(filename):
    return get_file_contents(filename, mode="rb")


def get_lambda_fullpath(lambda_function):
    from os import path
    lambda_directory = path.abspath(
        path.join(path.dirname(__file__), ".." + os.path.sep + ".." + os.path.sep + "lambda_functions"))
    return path.realpath(path.join(lambda_directory, lambda_function))


def get_os_temp_dir():
    import platform
    import tempfile
    # On MacOS, i.e. Darwin, tempfile.gettempdir() and os.getenv('TMPDIR') return a value
    # such as '/var/folders/nj/269977hs0_96bttwj2gs_jhhp48z54/T'; it is one that I do not want!
    return '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()


def remove_subdir(subdir):
    import shutil
    if os.path.exists(subdir):
        shutil.rmtree(subdir, ignore_errors=True)


def make_temp_subdir(subdir):
    os_temp_dir = get_os_temp_dir()
    fullpath = os.path.join(os_temp_dir, subdir)
    remove_subdir(fullpath)
    os.makedirs(fullpath)
    return fullpath


def traverse(pathname, d):
    """prints a given nested directory with proper indentation"""
    indent = ''
    for i in range(d):
        indent = indent + '  '
    for item in os.listdir(pathname):
        new_item = os.path.join(pathname, item)
        logger.info(indent + new_item)
        if os.path.isdir(new_item):
            traverse(new_item, d + 1)
