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

# Read other configuration from config.json
AWS_ACCOUNT_ID=$((RDB_ENV=test python3 "${ROOT}/cli.py" config "${LAMBDA}" account_id) 2>&1)
REGION=$((RDB_ENV=test python3 "${ROOT}/cli.py" config "${LAMBDA}" region) 2>&1)
RUNTIME=$((RDB_ENV=test python3 "${ROOT}/cli.py" config "${LAMBDA}" runtime) 2>&1)


ROLE="${LAMBDA}"
echo Creating role "${ROLE}" for "${LAMBDA}" begin...
trust="trust_policy_lambda.json"
echo "************************"
pwd
echo 1 aws iam create-role
aws iam create-role --role-name "${ROLE}" --assume-role-policy-document file://${trust}
sleep 5
echo "************************"
pwd
echo 2 aws iam update-assume-role-policy
aws iam update-assume-role-policy --role-name "${ROLE}" --policy-document file://configs/${trust}
sleep 5
echo "************************"

cd "lambda_functions/${LAMBDA}" || exit 1
pwd
echo 3 aws iam put-role-policy
aws iam put-role-policy --role-name "${ROLE}" --policy-name "${ROLE}" --policy-document file://iam.json
sleep 5
echo "************************"
echo Creating iam role "${ROLE}" end

# Create Lambda function
[[ -f "/tmp/${LAMBDA}.zip" ]] && rm -f "/tmp/${LAMBDA}.zip"
echo Zipping folder "${LAMBDA}"...
zip -r "/tmp/${LAMBDA}.zip" * -x .DS_Store -x config.json -x event.json -x iam.json -x requirements.txt -x API.*
cd "${ROOT}/../packages/${RUNTIME}/" || exit 1
pwd
zip -ur "/tmp/${LAMBDA}.zip" * -x "*.DS_Store"
cd "${ROOT}/.." || exit 1
pwd
[[ ${RUNTIME} == python* ]] && zip -ur "/tmp/${LAMBDA}.zip" api/rdb -x "*.DS_Store"

cd "${ROOT}/lambda_functions/${LAMBDA}" || exit 1
sleep 5 # To avoid errors
echo "************************"
pwd
HANDLER=$((RDB_ENV=test python3 "${ROOT}/cli.py" config "${LAMBDA}" handler) 2>&1)
echo 4 aws lambda create-function
aws lambda create-function \
        --function-name "${LAMBDA}" \
        --runtime ${RUNTIME} \
        --role "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA}" \
        --handler ${HANDLER} \
        --zip-file "fileb:///tmp/${LAMBDA}.zip" \
        --region "${REGION}"
sleep 5
aws lambda update-function-code \
  --function-name "${LAMBDA}" \
  --zip-file "fileb:///tmp/${LAMBDA}.zip" \
  --region "${REGION}"

# https://gist.github.com/andywirv/f312d561c9702522f6d4ede1fe2750bd
echo "5 Updating environment variables"
ENV_VARIABLES=$((RDB_ENV=test python3 "${ROOT}/cli.py" config "${LAMBDA}" environment_variables) 2>&1)
ENV_VARIABLES=$(echo "${ENV_VARIABLES}" | sed "s/\'/\"/g")
aws lambda update-function-configuration --function-name "${LAMBDA}" --region "${REGION}" --environment '{"Variables":{"RDB_ENV":"production","RDB_LOG_LEVEL":"INFO"}}'

rm "/tmp/${LAMBDA}.zip"
echo "************************"

cd ../.. || exit 1
