# demo-store-api
Demo Flask REST API with JWT Authentication for a Demo Online Store


## TODO
* Create a common docker image for auth, products and orders microservices.
* Add swagger UI
* Handle JWT errors from within Flask
* Add unit tests using pytest

## Build
To build the microservices using `docker-compose` by following the steps below,

  ```
  cd ~/path/to/demo-store-api/orchestra
  sudo docker-compose up -d
  ```
The above command will pull all docker images from docker hub and setup the networking, volumes as well as ports for the docker containers.


## Run
To run you can open a terminal and follow these commands,

  * Login and get JWT Token
  ```
  $ curl -H "Content-Type: application/json" -X POST -d '{"username":"user","password":"passwd"}' http://localhost:8000/auth/login
  {"access_token": "<ACCESS_TOKEN_HERE>", "refresh_token": "<REFRESH_TOKEN_HERE>"}
  ```
  
  * Get product
  ```
  $ curl -H "Content-Type: application/json" -X GET http://localhost:8000/api/v1.0/products/e32eeac1-df82-11e8-87d5-680715cce921
  {"message": "Product not found."}
  ```
  
  * Add product
  ```
  $ curl -X POST "http://localhost:8000/api/v1.0/products/" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer <ACCESS_TOKEN_HERE>" -d "{  \"uuid\": \"e32eeac1-df82-11e8-87d5-680715cce921\",  \"name\": \"New Product Name\",  \"price\": 777.33}"
  
  ```
  
  * Refresh JWT Token
  ```
  $ curl -X POST "http://localhost:8000/auth/refresh" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer <REFRESH_TOKEN_HERE>"
{"access_token": "<NEW_ACCESS_TOKEN_HERE>"}

  ```

  * Modify product
  ```
  $ curl -X PUT "http://localhost:8000/api/v1.0/products/f6713754-a5b2-4185-981f-caa94ca89dbd" -H "accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer <ACCESS_TOKEN_HERE>" -d "{  \"uuid\": \"f6713754-a5b2-4185-981f-caa94ca89dbd\",  \"name\": \"Modified New Product Name\",  \"price\": 555.33}"
  
  ```
