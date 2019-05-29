import logging


def lambda_logger(python_file_name, cwd, level=logging.INFO):
    """
    simplest logger that allows lambda environment variable to override logging level
    :param python_file_name: the source code filename of caller
    :param cwd: current working directory
    :param level: desired logging level, INFO is the default
    :return default log handler
    """
    import boto3
    import botocore
    from os import environ, listdir
    override_level = environ.get('RDB_LOG_LEVEL')
    if override_level is not None:
        # noinspection PyUnusedLocal, PyBroadException
        try:
            level = logging.getLevelName(override_level)
        except Exception as ex:
            pass

    logger = logging.getLogger(python_file_name)
    logger.setLevel(level)
    logger.info(cwd)
    logger.info(str(listdir(path=cwd)))

    logger.info("boto3 version:" + boto3.__version__)
    logger.info("botocore version:" + botocore.__version__)
    return logger
