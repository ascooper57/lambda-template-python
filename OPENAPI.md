OpenAPI: Swagger
================

The OpenAPI Specification was donated to the Linux Foundation under the OpenAPI Initiative in 2015. The specification creates a RESTful interface for easily developing and consuming an API by effectively mapping all the resources and operations associated with it. Swagger is a specification for documenting REST API. It specifies the format (URL, method, and representation) to describe REST web services. ... The methods, parameters, and models description are tightly integrated into the server code, thereby maintaining the synchronization in APIs and its documentation.

[What is Swagger and Why it Matters](https://blog.readme.io/what-is-swagger-and-why-it-matters/)

What Is Amazon API Gateway?
Amazon API Gateway is an AWS service for creating, publishing, maintaining, monitoring, and securing REST at any scale. API developers can create APIs that access AWS or other web services as well as data stored in the AWS Cloud. As an API Gateway API developer, you can create APIs for use in your own client applications (apps). Or you can make your APIs available to third-party app developers. For more information.

API Gateway creates REST APIs that:

* Are HTTP-based.

* Adhere to the REST protocol, which enables stateless client-server communication.

* Implement standard HTTP methods such as GET, POST, PUT, PATCH and DELETE.

* When used in conjunction with OpenAPI Swagger data models, the API Gateway is the single source of truth in a RESTful API system and the subsequent data requests and responses are bi-directionally enforced becoming a binding contract between the client and the backend Function as a Service Lambda inplementation.

Praktikós extends the usage of OpenAPI Swagger RESTFul defintions to automatically generate:

* Lambda Function as a Service (FaaS) source code
* Database table object source code
* Automated test source code for your Lambda Function as a Service
* Automated test source code for your Database table
* Automated provisioning of your Lambda Function as a Service into Amazon's IAM, Cognito, Lambda, API Gateway, CloudWatch technologies.

[OpenAPI Definitions of Sample API Integrated with a Lambda Function](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-as-lambda-proxy-export-swagger-with-extensions.html)

[Swagger RESTful API Documentation Specification](https://docs.swagger.io/spec.html)