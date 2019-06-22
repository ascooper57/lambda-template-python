#!/bin/bash
set -e

[[ -e src ]] && rm -rf src > /dev/null 2>&1

BUCKET=praktikos-template
ZIP_FILE=/tmp/praktikos-python-rdb.zip
echo "Sync content with S3 bucket ${BUCKET} start"
[[ -e ${ZIP_FILE} ]] && rm -f ${ZIP_FILE}
zip -r -X ${ZIP_FILE} . --exclude deploy.sh *.git* *.idea* .DS_Store api/.DS_Store api/*/.DS_Store api/*/*/.DS_Store *__pycache__* *.pyc
aws s3 cp ${ZIP_FILE} s3://${BUCKET} --cache-control "public, max-age=31536000" --acl public-read
[[ -e ${ZIP_FILE} ]] && rm -f ${ZIP_FILE}
echo "Sync content with S3 bucket ${BUCKET} end"


BUCKET=praktikos-media
ZIP_FILE=0_TEST_PUBLISH_CODE.zip
[[ -e ${ZIP_FILE} ]] && rm -f ${ZIP_FILE}
zip -r -X ${ZIP_FILE} . --exclude deploy.sh *.git* *.idea* .DS_Store api/.DS_Store api/*/.DS_Store api/*/*/.DS_Store *__pycache__* *.pyc .gitignore .travis.yml API.json API.yaml Dockerfile ISSUE_TEMPLATE.md MANIFEST.in pytest.ini README.md requirements.txt setup.py tox.ini

aws s3 cp ${ZIP_FILE} s3://${BUCKET} --cache-control "public, max-age=31536000" --acl public-read
[[ -e ${ZIP_FILE} ]] && rm -f ${ZIP_FILE}
echo "Sync content with S3 bucket ${BUCKET} end"

