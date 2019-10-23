#!/usr/bin/env bash

CWD=$(pwd)
DOWNLOADS=~/Downloads
PRAKTIKOS_HOME="${CWD}/../"

echo Prepare "${DOWNLOADS}" folder
pushd "${DOWNLOADS}" || exit 1
rm -rf "${DOWNLOADS}"/praktikos-template-python > /dev/null
mkdir -p "${DOWNLOADS}"/praktikos-template-python

echo "Unzip generated files"
cd praktikos-template-python || exit 1
unzip ../praktikos-template-python.zip
cd "${DOWNLOADS}" || exit 1
ditto -V praktikos-template-python ${PRAKTIKOS_HOME}

echo "Merge and run automated tests on generated code changes"
cd "${PRAKTIKOS_HOME}" || exit 1
cp -pf api/rdb/model/model_list.py.MERGE api/rdb/model/model_list.py
cp -pf "${CWD}/event.json" api/lambda_functions/LambdaApiGenerated/event.json

RDB_ENV=test py.test test/units/table_generated_test.py
RDB_ENV=test py.test test/units/LambdaApiGenerated_test.py
echo RDB_ENV=test py.test --verbose test
