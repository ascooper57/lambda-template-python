praktikos-python-rdb
================

[![Travis][build-badge]][build]
[![Coveralls][coveralls-badge]][coveralls]

[build-badge]: https://travis-ci.com/praktikos/praktikos-python-rdb.svg?token=ULzyak4HQDRjWMeE2ZaM&branch=master
[build]: https://travis-ci.com/praktikos/praktikos-python-rdb
    
[coveralls-badge]: https://img.shields.io/coveralls/praktikos/praktikos-python-rdb/master.png?style=flat-square
[coveralls]: https://coveralls.io/github/praktikos/praktikos-python-rdb

<img src="http://online.swagger.io/validator?url=https://api.praktikos.com/swagger">

API Gateway implemented with Lambda, Cognito and RDS (Postgres)

## Getting Started

```bash
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    xcode-select --install
    brew update
    brew upgrade

    brew install python3
    python3 --version 
        Python 3.7.0
        
    brew services stop postgresql
    brew uninstall -force postgresql
    rm -rf /usr/local/var/postgres
    
    brew install postgresql
    postgres --version
        postgres \(PostgreSQL\) 9.6.5 
            
    psql --version
        psql (PostgreSQL) 11.2

    createdb praktikos_test -U `whoami`
    psql -c 'CREATE DATABASE praktikos_test;' -U `whoami`
    psql -c 'CREATE EXTENSION hstore;' praktikos_test -U `whoami`
    Add a register_hstore parameter to PostgresqlExtDatabase.
    psql --host localhost praktikos_test
     \dx
                                     List of installed extensions
  	Name   | Version |   Schema   |                             Description                             
	---------+---------+------------+---------------------------------------------------------------------
 	hstore  | 1.4     | public     | data type for storing sets of (key, value) pairs
 	plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
                  
    praktikos_test=# SELECT PostGIS_Version();
            postgis_version            
	---------------------------------------
 	2.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
	(1 row)
               
    pip install -U pytest
    py.test --version
        This is pytest version 3.1.3, imported from /usr/local/lib/python3.6/site-packages/pytest.py
            setuptools registered plugins:
        pytest-pep8-1.0.6 at /usr/local/lib/python3.6/site-packages/pytest_pep8.py
        pytest-cov-2.3.1 at /usr/local/lib/python3.6/site-packages/pytest_cov/plugin.py   

    pgadmin4 https://www.postgresql.org/ftp/pgadmin/pgadmin4/v2.0/macos/  

```

### file ~/.aws/credentials

Ask for credentails for AWS from Andy or Andy

```
  [default]
  output = json
  region = us-east-1
  aws_access_key_id = ********************
  aws_secret_access_key = ****************************************
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

    brew install git
    git --version
        git version 2.20.1 (Apple Git-117)
    open https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
    brew install gpg
    gpg --version
        gpg \(GnuPG\) 2.2.1
        libgcrypt 1.8.1
    ssh-add -K ~/.ssh/id_rsa
    ssh-add -L
    git clone https://github.com/praktikos/praktikos-python-rdb.git
    cd praktikos-python-rdb
```

### OPTIONAL: .env

If you create an .env file at the root of the project, you can add the RDB_ENV= and it will overrdie the env variable.

```bash
    cd praktikos-python-rdb
    echo RDB_ENV=test > .env
```

## Start Postgres

If you want to manually start and stop postgresql (installed via homebrew), the easiest way is:

```bash
    rm /usr/local/var/postgres/postmaster.pid
    brew services start postgresql

and

    brew services stop postgresql
```

## creating a new table in the production database

```bash
    cd praktikos-python-rdb

    RDB_ENV=test       ./cli.sh migrate
    RDB_ENV=production ./cli.sh migrate

    Table should now be in production with the requesite test data in it.
```

### to run tests
```bash
    cd praktikos-python-rdb
    
To run an individual unit test
    RDB_ENV=test py.test test/units/schema_test.py

OR
to run all unit tests
    RDB_ENV=test py.test --verbose test
```


### to run tests

```bash
    cd praktikos-python-rdb

TO run a unit test
    RDB_ENV=test py.test test/units/LambdaApiHealth_test.py

OR to run all unit tests
    RDB_ENV=test py.test --verbose test
```

# Extras

## Optionally Setting up a Docker environment to update dependencies
        
```bash
	brew install docker
	docker --version
	
    cd praktikos-python-rdb
    docker build -t praktikos-python-rdb .
    docker images
    docker ps
    docker run -it -v `pwd`:/mnt --entrypoint=/bin/bash  praktikos-python-rdb
    (you are automatically put into: /mnt )
```
```bash
    namo ~/.aws/credentials
        [default]
        output = json
        region = us-east-1
        aws_access_key_id = ********************
        aws_secret_access_key = ****************************************
    ^o
    ^x
    (to run test suite:)
    pip3 install -r requirements.txt 
    /etc/init.d/postgresql restart
    RDB_ENV=test py.test --verbose test
```
```bash
    if you need to update python packages dependencies to be deployed with your lambda function(s)
        open http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html

    cd packages/python3.7
    pip3 install psycopg2-binary --upgrade -t /mnt/packages/python3.7/
    pip3 install peewee --upgrade -t /mnt/packages/python3.7/
    pip3 install requests --upgrade -t /mnt/packages/python3.7/
```

#### Optionally Cleaning up a Docker environment

```bash
   docker rmi $(docker images -q) --force
   docker rm -v $(docker ps -qa)
```

## Optionally View API via Swagger

```bash
    open https://chrome.google.com/webstore/detail/swagger-ui-console/ljlmonadebogfjabhkppkoohjkjclfai?hl=en
    download and install into your Chrome browser: Swagger2Puml UI Console
    Once installed into Chrome, Click the lime green button to the right of the URL input area 
    In type in box, enter: https://###########.execute-api.us-east-1.amazonaws.com/v1/swagger
    Click "explore" button
```

## Optionally Generate a Plant UML representation of your API

![excerpt of the petstore example](petstore_example/swagger.png)

To create a diagram call the script with:

```bash
    brew cask install java
    java --version
        java 10.0.2 2018-07-17
        
    brew install plantuml
        plantuml -version
        PlantUML version 1.2018.03 \(Thu Apr 05 09:59:15 PDT 2018\)

    brew install graphviz
        /usr/local/Cellar/graphviz/2.40.1
        
    brew install plantuml graphviz
    plantuml -version
    PlantUML version 1.2018.08 (Sun Jun 24 05:31:00 PDT 2018)
    (GPL source distribution)
    Java Runtime: Java(TM) SE Runtime Environment
    JVM: Java HotSpot(TM) 64-Bit Server VM
    Java Version: 1.8.0_71-b15
    Operating System: Mac OS X
    OS Version: 10.13.6
    Default Encoding: UTF-8
    Language: en
    Country: US
    Machine: Alan-Cooper-MBP-2.local
    PLANTUML_LIMIT_SIZE: 4096
    Processors: 8
    Max Memory: 3,817,865,216
    Total Memory: 257,425,408
    Free Memory: 248,029,560
    Used Memory: 9,395,848
    Thread Active Count: 1

    The environment variable GRAPHVIZ_DOT has been set to /usr/local/opt/graphviz/bin/dot
    Dot executable is /usr/local/opt/graphviz/bin/dot
    Dot version: dot - graphviz version 2.40.1 (20161225.0304)
    Installation seems OK. File generation OK    
    cd praktikos-python-rdb/api/rdb/utils
    python swagger_2_puml.py endpoints/sample.json > sample.puml
```

It will create the file `sample.puml` which can then be translated into a PNG image with PlantUML with:


```bash
    open http://plantuml.com/starting
    plantuml -help
    plantuml code_gen/endpoints/sample.puml -tpng
    plantuml code_gen/endpoints/sample.puml -ttxt
```

## Add PlantUML plugin to PyCharm

```
    Menu: PyCharm->Preferences->Plugins->PlantUML
```

# Debugging

## Debugging API Gateway

```bash
    If you see this error message, you have envoked the endpoint with the incorrect hppt verb (GET/PUT/POST/DELETE)
        HTTP/2 403 
        content-type: application/json
        content-length: 42
        date: Sat, 27 Jan 2018 19:58:09 GMT
        x-amzn-requestid: 65e9c202-039c-11e8-a263-3708ed51d1ef
        x-amzn-errortype: MissingAuthenticationTokenException
        x-cache: Error from cloudfront
        via: 1.1 c7b4131244863241121573ea02fc44ad.cloudfront.net (CloudFront)
        x-amz-cf-id: hSJGJ7JgPFGz3p5XZc4oFqo84Z9S09dYB9QZiHhmtnfkeJAJ0-GhKA==
        
     If you see any error messages Access-Control-Allow-Origin or anything CORS related, it is a red herring!
     Check the CloudWatch logs for that endpoint for the actual error. 
     
     For example: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logs:
```

## Debugging RDB / Postgres 

```
    If you see this error message, "current transaction is aborted, commands ignored until end of transaction block on PUT media"
	It usually means that there is a mismatch between the swagger definition and the RDB table definition
```
    
