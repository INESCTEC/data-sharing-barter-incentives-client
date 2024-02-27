# PREDICO  (Data Sharing / Barter Incentives) client.

A Dockerized interface for the https://github.com/CPES-Power-and-Energy-Systems/data-sharing-barter-incentives-rest-api 
Datamarket Server API.

The objective of this API software package is to provide an in-between assistance in the communication between the Datamarket client and the Datamarket Server API. 
Its goal is mainly to abstract the client from the complexity of the underlying Blockchain and IDS Dataspace technologies required 
to interact with the platform.

The client wallet will still be located in the client's machine, but the client will not need to interact with it directly.

> [!CAUTION]
> This package should be used exclusively for testing use cases purposes in testnet environments ONLY.

# Installation

You need first to get access to the PREDICO (Data Sharing / Barter Incentives) client repository and clone it to your local machine.
    
```shell
git clone https://github.com/CPES-Power-and-Energy-Systems/predico-data-sharing-barter-client.git
```

## Build docker image

Build docker image:

```shell
$ docker-compose build
```

## Run docker container

Run docker container image. This will start the python client API simulation tool:

```shell
$ docker-compose up
```

## Documentation

The documentation for the Predico Datamarket API can be found at: http://localhost:8000/docs

# Steps

The following steps are required to run the simulation tool and interact with the Predico Datamarket API.
It's advised to run the steps in the order they are presented.

You may use POSTMAN in order to interact with the API. The Postman collection can be found at: 
https://documenter.getpostman.com/view/391645/2s9YJZ5Qc7

1. Step 1: <strong>[USER]</strong> - Register a new user
2. Step 2: Validate email address
3. Step 3: <strong>[USER]</strong> - Login
4. Step 4: <strong>[WALLET]</strong> - Fund wallet
5. Step 5: <strong>[WALLET]</strong> - Register Wallet in the market
6. Step 6: <strong>[RESOURCE]</strong> - Create a new resource
7. Step 7: <strong>[MARKET]</strong> - Get list of sessions
8. Step 8: <strong>[MARKET]</strong> - Bid in an open session
9. Step 9: <strong>[MARKET]</strong> - Get market bid

