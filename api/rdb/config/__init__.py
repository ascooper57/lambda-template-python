# -*- coding: utf-8 -*-

import inspect
import logging
import os
import sys

from .config import Config, ConfigDict
from .environment import environments
from .exceptions import *
from .files import candidate_directories

logger = logging.getLogger(__name__)

# module config instance
_config = None


def init(module=None):
    """
    Initialize the config module by creating a Config instance.

    :param module: The name of your module (or program)
    """
    global _config
    environment = None
    # noinspection PyBroadException,PyUnusedLocal
    env_filepath = "../../.env"
    # noinspection PyBroadException,PyUnusedLocal
    try:
        env_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), env_filepath))
        with open(env_filepath) as f:
            k, v = f.readline().rstrip("\n").split("=")
            if k == "RDB_ENV":
                environment = v
    except Exception as ex:
        logger.info(env_filepath + " not found")

    try:
        if environment is None:
            logger.error(os.environ)
            environment = os.environ['RDB_ENV']
    except KeyError:
        environment = None
    if environment is None or len(environment) < 1:
        raise ConfigMissingEnvError("RDB_ENV must be set")

    if module is None:
        module = __guess_module()

    if module is None or not inspect.ismodule(module):
        raise ConfigMissingModuleError("module must be set")

    # cache the config values for the current config
    config_values = _config.config_values if _config is not None else None

    # build a new config object with the given settings
    _config = Config(environment=environment, module=module, config_values=config_values)


def get(key, default=None):
    """
    Returns the value for given key from the consolidated config.
    """
    global _config
    __check_init()
    return _config.get(key, default)


###

def environment():
    """
    Returns the environment string from the Config instance.
    """
    global _config
    __check_init()
    return _config.environment


def is_test():
    return environment() == 'test'


def is_staging():
    return environment() == 'staging'


def is_production():
    return environment() == 'production'


# A private method to call init() if necessary
def __check_init():
    global _config
    if _config is None:
        raise ConfigUnintialized("You must call init() first.")


# A private method for guessing a good name for the current module
def __guess_module():
    # noinspection PyProtectedMember
    package = sys._getframe(1).f_globals.get('__package__')
    module = sys.modules[package]
    return module
