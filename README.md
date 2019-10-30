praktikos-template-python
=========================

Functions as a Service implemented with API Gateway, Lambda, Cognito, S3, SNS and RDS (Postgres)

This is a software design paradigm shift

Published Swagger API for this project: <img src="http://online.swagger.io/validator?url=https://r1gzxipb32.execute-api.us-east-1.amazonaws.com/v1/swagger">

Table of Contents
=================

   * [praktikos-template-python](#praktikos-template-python)
   * [Table of Contents](#table-of-contents)
   * [Getting Started on Mac OS](#getting-started-on-mac-os)
   * [Familiar with Git?](#familiar-with-git)
   * [Optionally Getting Started on Docker](#optionally-getting-started-on-docker)
   * [AWS developer credentials](#aws-developer-credentials)
   * [Start Postgres](#start-postgres)
   * [Configure your Amazon Web Service's account for Praktikos](#configure-your-amazon-web-services-account-for-praktikos)
   * [Creating a new table in the production database](#creating-a-new-table-in-the-production-database)
   * [to run tests](#to-run-tests)
   * [RESTful API Code generation, provisioning and publication automation](#restful-api-code-generation-provisioning-and-publication-automation)
      * [1. Sign Up / Sign in](#1-sign-up--sign-in)
      * [2. Generate Code from example swagger file](#2-generate-code-from-example-swagger-file)
      * [3. Merge generated code into main project](#3-merge-generated-code-into-main-project)
      * [4. Publish API from newly generated code](#4-publish-api-from-newly-generated-code)
      * [5. Test RESTful API remotely deployed into Amazon Web Services](#5-test-restful-api-remotely-deployed-into-amazon-web-services)
   * [Contributing](#contributing)


Most applications are designed a three tiers. The thin top tier (front end) is the graphical user interface on your mobile device or desktop, the (backend) middle tier is the business logic / data base access functions and the bottom tier is the database (persisted object itself). Application Programming Interfaces (APIs) are commonly implemented as RESTful style endpoints. Each RESTful endpoint has one to four actions / verbs: GET, PUT, POST, DELETE. Middle tier endpoints can operate upon persisted data or contain your application's business logic.

A microservice splits a large monolithic application into several small, self-containing services. Amazon Web Services (AWS) introduced a technology named Functions as a Service (Lambda) which allows each API endpoint to be become a discrete self-contained stateless microservice. Developing and deploying correctly architected Lambda functions that meet enterprise-level standards of scalability, maintainability, and security is difficult and time consuming.

With our approach and toolset, AWS developers can automatically generate source and test code, then deploy a correct Functions as a Service backend, allowing you to focus their time and energy on building valuable business logic instead of wrangling with and debugging mundane, common, and routine code. We provide this open source project template to bootstrap Lambda Endpoint development. We also provide our tool Praktikós to publish these (and your future / custom Lambda Endpoints) into Amazon Web Services reducing or eliminating the need for you to become an expert in technologies such as RDS, S3, Cognito, IAM, Lambda, Api Gateway, CloudWatch, Simple Messaging Service.

We are not a runtime library. All Praktikós generated code utilizes native language libraries / packages / modules. Everything that is provisioned or installed in Amazon utilizes their native, pristine services

* `Secure User Management` Authentication and Authorization: Cognito authenticated RestFUL APIs create complete front-end / back-end isolation with per endpoint customized security
* `Scalability` CloudFront and API Gateway handles any number of global requests per second (RPS) while making good use of system resources
* `Logging / Traceability` CloudWatch collects and accesses all your performance and operational data in form of logs and metrics from a single platform.
* `Test Harness` User executes auto generated test automation suite for new RESTful Endpoint, locally and remotely
* `Common RESTful endpoints` template includes Lambda RESTful endpoints and automated tests for functions that are common these days as backend services
* `Unified Modeling Language` Auto generated from Swagger definitions, always up-to-date, UML View of entire API


| Name	             | Description                                                                                     |
|:-------------------|:------------------------------------------------------------------------------------------------|
| Handler	         | When a Lambda function is invoked, AWS Lambda starts executing your generated code by calling the handler function. AWS Lambda passes any event data to this handler as the first parameter. Your handler should process the incoming event data and may invoke any other functions/methods in your code. |
| Invocation Context | Your Lambda handler function is also passed a context object to the handler function, as the second parameter. Via this context object your code can interact with the Lambda service itself. |
| Logging            | Your Lambda function can contain logging statements. Lambda writes these logs to CloudWatch Logs. Specific language statements generate log entries, depending on the language you use to author your Lambda function code. |
| Exceptions         | Your Lambda function needs to communicate the result of the function execution to Lambda. Depending on the language you author your Lambda function code, there are different ways to end a request successfully or to notify Lambda an error occurred during execution. The Swagger data models are enforced by the API Gateway preventing malformed RESTful requests and responses; a common cause of Exceptions. |
| Stateless          |Your Lambda function code must be written in a stateless style, and have no affinity with the underlying compute infrastructure. Your code should expect local file system access, child processes, and similar artifacts to be limited to the lifetime of the request. Persistent state should be stored in PostgresSql, Amazon S3, Amazon DynamoDB, or another cloud storage service. Requiring functions to be stateless enables Lambda to launch as many copies of a function as needed to scale to the incoming rate of events and requests. These functions may not always run on the same compute instance from request to request, and a given instance of your Lambda function may be used more than once by Lambda. |


Our Core Principals

* End-to-end Application design should come from a *single* source of truth that describes the interaction of how the user facing frontend and data providing backend enforcing what each expects to receive/send via a OpenAPI (Swagger) data model
* We suggest that user-facing frontend *should* be built against a backend system of distributed, stateless, atomic functions that are infinitely scalable, easy to maintain and reuse
* 70% of an application's backend is typically built on common, routine functionality. The remaining 30% is the "secret sauce" - business logic that makes the application valuable and specific to the organization building it
* Developers shouldn’t expend time on routine coding - Managers should leverage developers to focus on the features / functionality (creative, fun, special) aspects of application coding, not the framework - the common, error prone, routine parts of the application. For these common, routine parts, they welcome an automation solution.
* Automation of the backend data services improves quality and reduces Time to Market (TTM)
* Modification of any atomic backend service should not disturb the overall integrity of the system thereby reducing re-certification efforts and overall risk - endure stresses of the entire application lifecycle
* A monolith is a service that has more than one restful endpoint OR is stateful (in the backend). Tends to have more permissions, resources (memory, cpu) than each actually needs to execute properly thereby reducing threat profile for each endpoint
* Should be able to track the cost of *each* endpoint execution and make business decisions around the Return of Investment (ROI) of that endpoint. (in a true microservices application)

# Getting Started on Mac OS

```bash
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    xcode-select --install
    brew update
    brew upgrade

    brew install python3
    python3 --version 
        Python 3.7.4
                   
    pip3 install -U pytest
    py.test --version
	This is pytest version 4.5.0, imported from /usr/local/lib/python3.7/site-packages/pytest.py

    brew install awscli
    aws --version
        aws-cli/1.16.260 Python/3.7.4 Darwin/19.0.0 botocore/1.12.250

    brew services stop postgresql
    brew uninstall -force postgresql
    rm -rf /usr/local/var/postgres
    
    brew install postgresql
    brew postgresql-upgrade-database
    postgres --version
        postgres \(PostgreSQL\) 11.5
            
    psql --version
        psql (PostgreSQL) 11.5

    createdb praktikos_test -U `whoami`
    psql -c 'CREATE EXTENSION hstore;' praktikos_test -U `whoami`
    psql --host localhost praktikos_test
     \dx
                                     List of installed extensions
  	Name   | Version |   Schema   |                             Description                             
	---------+---------+------------+---------------------------------------------------------------------
 	hstore  | 1.5     | public     | data type for storing sets of (key, value) pairs
 	plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language

    Optional pgadmin4 
    open https://www.postgresql.org/ftp/pgadmin/pgadmin4/v2.0/macos/
```

# Familiar with Git?

Checkout this repo, then install dependencies with the following:

```
check to make sure your github key has been added to the ssh-agent list.  Here's my ~/.ssh/config file

 Host github.com github
     IdentityFile ~/.ssh/id_rsa
     IdentitiesOnly yes
     UseKeyChain yes
     AddKeysToAgent yes
```

```bash
    ssh-add -K ~/.ssh/id_rsa
    ssh-add -L
    git clone https://github.com/praktikos/praktikos-template-python.git
    cd praktikos-template-python
    pip3 install -r requirements.txt
```

# Optionally Getting Started on Docker

see DOCKER.md

# AWS developer credentials

When you interact with AWS, you specify your AWS security credentials to verify who you are and whether you have permission to access the resources that you are requesting. AWS uses the security credentials to authenticate and authorize your requests. Access keys consist of two parts: an access key ID (for example, AKIAIOSFODNN7EXAMPLE) and a secret access key (for example, wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). You use access keys to sign programmatic requests that you make to AWS if you use AWS CLI commands (using the SDKs) or using AWS API operations.

```bash
open https://console.aws.amazon.com/iam/home?#/security_credentials

aws configure

AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

```bash
more ~/.aws/credentials

[default]
aws_account_id=1234567890
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region=us-east-1
output=json

```
# Start Postgres

If you want to manually start and stop postgresql (installed via homebrew), the easiest way is:

```bash
cd pratikos-python-rdb/bin
./start_postgres.sh

OR

./stop_postgres.sh
```

# Configure your Amazon Web Service's account for Praktikos

```bash
cd praktikos-template-python
pip3 install -r requirements.txt
cd praktikos-template-python/api
RDB_ENV=test ./cli/py configure
```
# Creating a new table in the production database

Once your project works against your local database, it is time to create a cloud based / internet accessbile "production" database.

```bash
cd praktikos-template-python/api
vim config.json

(Edit section with your internet accessible database)
  "production": {
    "database": "praktikos",
    "host": "XXXXXXXXX-production-cluster.cluster-XXXXXXXXXXXX.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "username": "sa",
    "password": "ChangeMe!",
    "max_connections": 10000,
    "stale_timeout": 300,
    "sslmode": "allow"
  }

RDB_ENV=test       ./cli.py migrate
RDB_ENV=production ./cli.py migrate

Table should now be in production with the requesite test data in it.
```

# to run tests

Verify the integrity of the project by running the test suite locally against your locally installed Postgres database

```bash
cd praktikos-template-python

TO run a unit test
RDB_ENV=test py.test test/units/LambdaApiHealth_test.py

OR to run all unit tests
RDB_ENV=test py.test --verbose test
```

# RESTful API Code generation, provisioning and publication automation

## 1. Sign Up / Sign in

```bash
open https://client.praktikos.com
```

## 2. Generate Code from example swagger file

   * In the browser window side panel, Click "Generate Code"
   * Click in dashed line box "Drag SWAGGER JSON file here..."
   * Navigate to the file: praktikos-template-python/example/swagger.json
   * Click the "Next" button
   * Click the "Finish" button after generated code is downloaded

## 3. Merge generated code into main project

open up a Terminal (shell) window

```bash
cd praktikos-template-python/example
./merge_after_codegen.sh
```

## 4. Publish API from newly generated code


   * Zip up the main project (merged) ~/praktikos-template-python.zip
   * In the browser window side panel, Click "Publish API"
   * Click in dashed line box "Drag Zip file here..."
   * Navigate to the file: praktikos-template-python.zip
   * Click the "Next" button
   * Click on "LambdaApiGenerated"
   * Click the "Next" button
   * wait patiently about a minute
   * Click the "Finish" button after API is provisioned and published
   
## 5. Test RESTful API remotely deployed into Amazon Web Services

open up a Terminal (shell) window

```bash
cd praktikos-template-python/example
./test_published.sh
```

# Contributing

1. Fork it
2. Create your feature branch (`git checkout -b your_github_name-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Make sure to add tests for it. This is important so we don't break it in a future version unintentionally.
5. Push to the branch (`git push origin my-new-feature`)
6. Create new Pull Request
