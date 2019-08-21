#!/bin/bash

CWD=`pwd`
DOWNLOADS=~/Downloads
PRAKTIKOS_HOME=${CWD}/../

echo "Prepare ${DOWNLOADS} folder"
pushd ${DOWNLOADS}
rm -rf ${DOWNLOADS}/praktikos-python-rdb > /dev/null
mkdir -p ${DOWNLOADS}/praktikos-python-rdb

echo "Unzip generated files"
cd praktikos-python-rdb
unzip ../praktikos-python-rdb.zip
cd ${DOWNLOADS}
ditto -V praktikos-python-rdb ${PRAKTIKOS_HOME}

echo "Merge and run automated tests on generated code changes"
cd ${PRAKTIKOS_HOME}
cp -pf api/rdb/model/model_list.py.MERGE api/rdb/model/model_list.py
cp -pf ${CWD}/event.json api/lambda_functions/LambdaApiGenerated/event.json

RDB_ENV=test py.test test/units/table_generated_test.py
RDB_ENV=test py.test test/units/LambdaApiGenerated_test.py
#RDB_ENV=production py.test test/units/table_generated_test.py
echo RDB_ENV=test py.test --verbose test
