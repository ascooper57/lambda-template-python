Debugging
=========

# View API via Swagger

```bash
    open https://chrome.google.com/webstore/detail/swagger-ui-console/ljlmonadebogfjabhkppkoohjkjclfai?hl=en
    download and install into your Chrome browser: Swagger2Puml UI Console
    Once installed into Chrome, Click the lime green button to the right of the URL input area 
    In type in box, enter: https://###########.execute-api.us-east-1.amazonaws.com/v1/swagger
    Click "explore" button
```

# Debugging API Gateway
open up a Terminal (shell) window

```bash
    If you see this error message, you have invoked the endpoint with the incorrect http verb (GET/PUT/POST/DELETE)
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
cd praktikos-python-rdb/example
./test_published.sh
```

```
    If you see this error message afteryou have invoked the endpoint with the http verb (GET/PUT/POST/DELETE)
	HTTP/2 403 Invalid request body
    you have invoked the verb GET/PUT/POST/DELETE with the incorrect data (parameters / body) that it was expecting.
    In the swagger model, the "required" data is not present in the request or the lambda function's implementation is referencing data it did not receive in the request. 
```

# Debugging RDB / Postgres 

```
    If you see this error message, "current transaction is aborted, commands ignored until end of transaction block on PUT media"
	It usually means that there is a mismatch between the swagger definition and the RDB table definition
```


# Optionally Generate a Plant UML representation of your API

![excerpt of the petstore example](petstore_example/swagger.png)


To create a diagram call the script with:
   * In the browser window side panel, Click "Generate Code"
   * Click in dashed line box "Drag SWAGGER JSON file here..."
   * Navigate to the file: praktikos-python-rdb/example/swagger.json
   * Click the "Next" button
   * Click the "Finish" button after generated code is downloaded

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
