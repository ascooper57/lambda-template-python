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

## Getting Started on Mac OS

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

# RESTful API Code generation, provisioning and publication automation


## 1. Sign Up / Sign in

```bash
    open https://client.praktikos.com
```

## 2. Generate Code from example swagger file

   * In the browser window side panel, Click "Generate Code"
   * Click in dashed line box "Drag SWAGGER JSON file here..."
   * Navigate to the file: praktikos-python-rdb/example/swagger.json
   * Click the "Next" button
   * Click the "Finish" button after generated code is downloaded

## 3. Merge generated code into main project

open up a Terminal (shell) window

```bash
cd praktikos-python-rdb/example
./merge_after_codegen.sh
```

## 4. Publish API from newly generated code

   * Zip up the main project (merged) ~/praktikos-python-rdb.zip
   * In the browser window side panel, Click "Publish API"
   * Click in dashed line box "Drag Zip file here..."
   * Navigate to the file: praktikos-python-rdb.zip
   * Click the "Next" button
   * Click on "LambdaApiGenerated"
   * Click the "Next" button
   * wait patiently about a minute
   * Click the "Finish" button after API is provisioned and published
   
## 5. Test RESTful API

open up a Terminal (shell) window

```bash
cd praktikos-python-rdb/example
./test_published.sh
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b your_github_name-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Make sure to add tests for it. This is important so we don't break it in a future version unintentionally.
5. Push to the branch (`git push origin my-new-feature`)
6. Create new Pull Request
