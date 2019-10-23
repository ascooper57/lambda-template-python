#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "No argument supplied"
  exit 1
fi

LAMBDA=$1

# Check if the AWS CLI is in the PATH
found=$(which aws)
if [ -z "$found" ]; then
  echo "Please install the AWS CLI under your PATH: http://aws.amazon.com/cli/"
  exit 1
fi

ROOT=$(pwd)
find . -name __pycache__ -type d -exec rm -rf {} \; >> /dev/null 2>&1 

# Read other configuration from rdb/config/config.json
REGION=$((RDB_ENV=test python3 "${ROOT}"/cli.py config "${LAMBDA}" region) 2>&1)
RUNTIME=$((RDB_ENV=test python3 "${ROOT}"/cli.py config "${LAMBDA}" runtime) 2>&1)

# Updating Lambda functions
# ./create_python_links.py "${LAMBDA}"
cd lambda_functions || exit 1

[[ -f /tmp/"${LAMBDA}".zip ]] && rm -f /tmp/"${LAMBDA}".zip
echo Zipping folder "${LAMBDA}"...
cd "${LAMBDA}" || exit 1
zip -r /tmp/"${LAMBDA}".zip * -x .DS_Store -x config.json -x event.json -x iam.json -x requirements.txt -x API.*
cd "${ROOT}"/../packages/"${RUNTIME}"/ || exit 1
pwd
zip -ur /tmp/"${LAMBDA}".zip * -x "*.DS_Store"
cd "${ROOT}"/.. || exit 1
pwd
zip -ur /tmp/"${LAMBDA}".zip api/config.json
[[ "${RUNTIME}" == python* ]] && zip -ur /tmp/"${LAMBDA}".zip api/rdb -x "*.DS_Store"

echo Updating function "${LAMBDA}" begin...
cd "${ROOT}"/lambda_functions/"${LAMBDA}" || exit 1
aws lambda update-function-code --function-name "${LAMBDA}" --zip-file fileb:///tmp/"${LAMBDA}".zip --region "${REGION}"
rm /tmp/"${LAMBDA}".zip
echo Updating function "${LAMBDA}" end

# Create IAM Roles for Lambda Function
echo Updating role "${LAMBDA}" begin...
aws iam update-assume-role-policy --role-name "${LAMBDA}" --policy-document file://"${ROOT}"/configs/trust_policy_lambda.json
aws iam put-role-policy --role-name "${LAMBDA}" --policy-name "${LAMBDA}" --policy-document file://"${ROOT}"/lambda_functions/"${LAMBDA}"/iam.json
echo Updating role "${LAMBDA}" end

echo "Updating environment variables"
# https://gist.github.com/andywirv/f312d561c9702522f6d4ede1fe2750bd
ENV_VARIABLES=$((RDB_ENV=test python3 "${ROOT}"/cli.py config "${LAMBDA}" environment_variables) 2>&1)
ENV_VARIABLES=$(echo "${ENV_VARIABLES}" | sed "s/\'/\"/g")
aws lambda update-function-configuration --function-name "${LAMBDA}" --environment '{"Variables":{"RDB_ENV":"production","RDB_LOG_LEVEL":"INFO"}}'

cd .. || exit 1
