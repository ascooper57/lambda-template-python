#!/bin/bash

ARRAY=()
# get list of Lambda functions
pushd lambda_functions || exit 1
for LAMBDA in $(ls -1); do
  if [ -d "${LAMBDA}" ]; then
    ARRAY+=("${LAMBDA}")
  fi
done
popd || exit 1

for LAMBDA in "${ARRAY[@]}"; do ./deploy_lambda.sh "${LAMBDA}"; done
