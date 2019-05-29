# -*- coding: utf-8 -*-
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cwd = os.getcwd()
logger.info(cwd)
logger.info(str(os.listdir(path=".")))


def compute_hash(password_clear, password_salt):
    """
    Password administration
    :param password_clear the clear text password from the user
    :param password_salt the password salt to be applied to the password to create a has
    :return a hexidecimal hased password
    """
    import hashlib
    import binascii
    logger.info('Calling compute_hash')
    # Bytesize
    digest = hashlib.sha256
    bin_password = password_clear.encode()
    bin_salt = password_salt.encode()
    iterations = 4096
    dklen = 128
    # http://www.programcreek.com/python/example/74846/hashlib.pbkdf2_hmac
    dk = hashlib.pbkdf2_hmac(digest().name, bin_password, bin_salt, iterations, dklen)
    return binascii.hexlify(dk).decode('ascii')
