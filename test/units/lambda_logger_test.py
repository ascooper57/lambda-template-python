from api.rdb.utils.lambda_logger import lambda_logger


# noinspection PyCallingNonCallable
def test_lambda_logger():
    from os import getcwd, environ
    cwd = getcwd()
    import logging
    override_level = environ.get('RDB_LOG_LEVEL')
    if override_level is None:
        # https://AWS CloudWatch log files.aws.amazon.com/cloudwatch/home?region=us-east-1#logs:
        logger = lambda_logger(__name__, cwd)
        assert logger.isEnabledFor(logging.INFO)
        logger.info("This info logger message should be visible in the AWS CloudWatch log files")
        logger = lambda_logger(__name__, cwd, level=logging.INFO)
        assert logger.isEnabledFor(logging.INFO)
        logger.info("This info logger message should be visible in the AWS CloudWatch log files")
        logger = lambda_logger(__name__, cwd, level=logging.ERROR)
        assert logger.isEnabledFor(logging.ERROR)
        logger.info("This info logger message should be visible in the AWS CloudWatch log files")
        assert not logger.isEnabledFor(logging.INFO)
        logger.info("This info logger message should NOT be visible in the AWS CloudWatch log files")
    else:
        print("Test can't be executed properly because RDB_LOG_LEVEL is set which overrides API setting")
