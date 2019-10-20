#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is dirty hack to the distutils hard link problem
# see: http://bugs.python.org/issue8876
import os

del os.link

# can't wait for distutils2
from setuptools import setup

REQUIRES = ['boto3', 'botocore', 'psycopg2', 'peewee' ]

SCRIPTS = []

setup(name='praktikos-template-python',
      version='0.1',
      description='API Lambda and Database backend implementation',
      author='',
      author_email='',
      url='https://github.com/praktikos/praktikos-template-python.git',
      packages=['api'],
      install_requires=REQUIRES,
      # scripts=SCRIPTS,
      entry_points='''
        [console_scripts]
        api=api.cli:invoke
      ''',
      include_package_data=True,
      zip_safe=False,
      )
