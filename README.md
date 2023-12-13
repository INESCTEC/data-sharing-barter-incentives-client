# PREDICO  (Data Sharing / Barter Incentives) client.

A Dockerized interface for the Datamarket API.

The objective of this API software package is to provide an in-between assistance in the communication between the Datamarket client and the Datamarket Server API. 
Its goal is mainly to abstract the client from the complexity of the underlying Blockchain technologies required to interact with the platform.

The client wallet will still be located in the client's machine, but the client will not need to interact with it directly.

> [!CAUTION]
> This package should be used exclusively for testing use cases purposes in testnet environments ONLY.

# Installation

You need first to get access to the PREDICO (Data Sharing / Barter Incentives) client repository and clone it to your local machine.
    
```shell
git clone https://github.com/CPES-Power-and-Energy-Systems/predico-data-sharing-barter-client.git
```

## Environment variables

You should not be required to update any of the ENV variables, but in case you do, here's how:

- Go to `.env` file and update the default configuration:

Take a look to the following table with the .env variables and their description:

| Variable | Description |
| --- | --- |
| `IOTA_FAUCET_URL` | URL of the IOTA Faucet |
| `IOTA_NODE_URL` | URL of the IOTA Node |
| `TESTNET_ETH_NODE_URL` | URL of the Ethereum Node |
| `TESTNET_ETHERSCAN_API_KEY` | API key for Etherscan |
| `TESTNET_ETHERSCAN_URL` | URL of Etherscan |
| `TESTNET_ETH_ACCOUNT_ADDRESS` | Ethereum account address |
| `TESTNET_ETH_PRIVATE_KEY` | Ethereum account private key |
| `TESTNET_BATCH_CONTRACT_ADDRESS` | Ethereum batch contract address |
| `USERS_FILE_DIR` | Path to the users directory |
| `VALOREM_REST_HOST` | Host of the Valorem REST API |
| `VALOREM_REST_PORT` | Port of the Valorem REST API |
| `N_REQUEST_RETRIES` | Number of retries for the Valorem REST API |


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

### Swagger
The documentation for the Predico Datamarket API can be found at: http://localhost:8000/docs

### Postman

Documentation and Postman collection can be found at: https://documenter.getpostman.com/view/391645/2s9YJZ5Qc7

# Steps

The following steps are required to run the simulation tool and interact with the Predico Datamarket API.
It's advised to run the steps in the order they are presented.

## Register a new user

It is required to register a new user before any other operation can be performed. 
This is done by sending a POST request to the `/user/register_user/` endpoint.
Once the user is registered, the user's wallet is created and the user's seed is stored in the `files/users/` directory 
mapped to the docker container.

[//]: # (After a sucessful registration, the user's wallet is funded with 1000 IOTA tokens from the )

[//]: # ([IOTA Faucet]&#40;https://faucet.chrysalis-devnet.iota.cafe/&#41; and the email **must be validated** &#40;check your email&#41;.)

**Warning:** the user's password to access the wallet is stored in plain text. 
This is done for simplicity and tests purposes only.

```python

import requests
import json

url = f"http://localhost:8000/user/register_user/"

payload = json.dumps({
  "email": "andre.f.garcia@inesctec.pt",
  "password": "1234567890!",
  "password_conf": "1234567890!",
  "first_name": "Andre",
  "last_name": "Garcia",
  "role": [
    "buyer",
    "seller"
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

```

## Register a new resource

After a user is registered, it is possible to create a resource. 
This is done by sending a POST request to the `/resource/register_resource/` endpoint.
The resource is created and stored in the `files/users/` directory mapped to the docker container.


```python
import requests
import json

url = "http://localhost:8000/resource/register_resource/"

payload = json.dumps({
  "email": "andre.f.garcia@inesctec.pt",
  "name": "teste-parque",
  "type": "measurements",
  "to_forecast": True
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

## Register wallet

To be able to receive payments or to bid in **OPEN** sessions for the data measurements contributions it is required for the client to register a wallet.

```python
import requests

url = "http://localhost:8000/wallet/register_wallet/?email=andre.f.garcia@inesctec.pt"

payload = ""
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

## Bid on a resource

### Fund wallet

To be able to bid on a resource, the client's wallet must be funded with IOTA tokens.

```python
import requests

url = "http://localhost:8000/wallet/fund_wallet/?email=andre.f.garcia@inesctec.pt"

payload = ""
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

After a resource is created and a session is **OPEN**, it is possible to bid on it.
This is done by sending a POST request to the `/session/bid/` endpoint.


```python
import requests
import json

url = "http://localhost:8000/session/bid/"

payload = json.dumps({
  "email": "andre.f.garcia@inesctec.pt",
  "price": 110000000,
  "max_payment": 110000000,
  "resource": 7
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

## Fund wallet

To be able to bid on a resource, the client's wallet must be funded with IOTA tokens. 
You can also withdraw tokens from the [IOTA Faucet](https://faucet.chrysalis-devnet.iota.cafe/) giving the client's 
wallet address.

```python
import requests

url = "http://localhost:8000/wallet/fund_wallet/?email=andre.f.garcia@inesctec.pt"

payload = ""
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

## Contribute with data measurements

You can contribute with measurements for the overall effort of the Datamarket engine by sending a 
POST request to the `/data/send_measurements/` endpoint.
At the end of each session user contributions are evaluated and contributions may be rewarded with IOTA tokens in case 
they are considered valid and useful for the overall effort of the Datamarket engine.

```python
import requests
import json

url = "http://localhost:8000/data/send_measurements/"

payload = json.dumps({
  "email": "andre.f.garcia11@example.com",
  "resource_name": "teste-parque-4",
  "time_interval": 60,
  "aggregation_type": "avg",
  "units": "kw",
  "timeseries": [
    {
      "datetime": "2020-01-01 00:00:00",
      "value": "1.0"
    },
    {
      "datetime": "2020-01-01 01:00:00",
      "value": "2.0"
    }
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

# Wallet and Client configs

The client's wallet and configurations by default are stored in the `files/users/` directory mapped to 
the docker container.

# Logging

The client's logs are stored in the `files/logfile.log/` directory mapped to the docker container.
To best understand the client's behaviour, it is advised to check the logs.