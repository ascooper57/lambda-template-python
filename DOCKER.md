Docker
======

# Optionally Setting up a Docker environment
        
```bash
	brew install docker
	docker --version
	
    cd lambda-template-python
    docker build -t lambda-template-python .
    docker images
    docker ps
    docker run -it -v `pwd`:/mnt --entrypoint=/bin/bash  lambda-template-python
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

## Optionally Cleaning up a Docker environment

```bash
   docker rmi $(docker images -q) --force
   docker rm -v $(docker ps -qa)
```
