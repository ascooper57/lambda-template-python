praktikos-template-python
====================

API Gateway implemented with Lambda, Cognito, S3, SNS and RDS (Postgres)

<img src="http://online.swagger.io/validator?url=https://r1gzxipb32.execute-api.us-east-1.amazonaws.com/v1/swagger">

## Getting Started on Mac OS

```bash
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    xcode-select --install
    brew update
    brew upgrade

    brew install python3
    python3 --version 
        Python 3.7.4
        
    brew install awscli
    aws --version
        aws-cli/1.16.260 Python/3.7.3 Darwin/18.6.0 botocore/1.12.170

    brew services stop postgresql
    brew uninstall -force postgresql
    rm -rf /usr/local/var/postgres
    
    brew install postgresql
    brew postgresql-upgrade-database
    postgres --version
        postgres \(PostgreSQL\) 11.4
            
    psql --version
        psql (PostgreSQL) 11.4

    createdb praktikos_test -U `whoami`
    psql -c 'CREATE EXTENSION hstore;' praktikos_test -U `whoami`
    Add a register_hstore parameter to PostgresqlExtDatabase.
    psql --host localhost praktikos_test
     \dx
                                     List of installed extensions
  	Name   | Version |   Schema   |                             Description                             
	---------+---------+------------+---------------------------------------------------------------------
 	hstore  | 1.5     | public     | data type for storing sets of (key, value) pairs
 	plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
                  
    pip3 install -U pytest
    py.test --version
	This is pytest version 5.0.1, imported from /usr/local/lib/python3.7/site-packages/pytest.py

    pgadmin4 https://www.postgresql.org/ftp/pgadmin/pgadmin4/v2.0/macos/  

```

## Optionally Getting Started on Docker

see DOCKER.md

### file ~/.aws/credentials
When you interact with AWS, you specify your AWS security credentials to verify who you are and whether you have permission to access the resources that you are requesting. AWS uses the security credentials to authenticate and authorize your requests. Access keys consist of two parts: an access key ID (for example, AKIAIOSFODNN7EXAMPLE) and a secret access key (for example, wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY). You use access keys to sign programmatic requests that you make to AWS if you use AWS CLI commands (using the SDKs) or using AWS API operations.

```bash
open https://console.aws.amazon.com/iam/home?#/security_credentials
```

```bash
aws configure
```

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

## Familiar with Git?
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


## Start Postgres

If you want to manually start and stop postgresql (installed via homebrew), the easiest way is:

```bash
rm /usr/local/var/postgres/postmaster.pid
brew services start postgresql

and

brew services stop postgresql
```

## Configure your Amazon Web Service's account for Praktikos

```bash
cd pratikos-python-rdb
pip3 install -r requirements.txt
cd src/praktikos-configure-aws/aws
./configure.py
```
## Creating a new table in the production database

```bash
cd praktikos-template-python

RDB_ENV=test       ./cli.sh migrate
RDB_ENV=production ./cli.sh migrate

Table should now be in production with the requesite test data in it.
```

### to run tests

```bash
cd praktikos-template-python
pip3 install -r requirements.txt

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
   
## 5. Test RESTful API

open up a Terminal (shell) window

```bash
cd praktikos-template-python/example
./test_published.sh
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b your_github_name-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Make sure to add tests for it. This is important so we don't break it in a future version unintentionally.
5. Push to the branch (`git push origin my-new-feature`)
6. Create new Pull Request
