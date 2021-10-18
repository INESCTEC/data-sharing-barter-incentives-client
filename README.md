# valorem-client-python

Python client simulation tools for VALOREM project 

**Warning: This package should be used exclusively for tests / debug purposes.**


## Install:

First, build docker container image: 


```shell
$ docker-compose build
```


Alternatively, you can also download the docker container from INESC TEC Gitlab Registry


1. Login into inesctec registry:


```shell
$ docker login docker-registry.inesctec.pt
```



2. Pull pre-built container image from registry:


```shell
$ docker-compose -f docker-compose.prod.yml pull
```
    

3. Update your ENV variables:

- Go to `.env` file and update REST connection configs:

```
VALOREM_REST_HOST=insert_rest_ip_here
VALOREM_REST_PORT=insert_rest_port_here
```

## Usage:

Second, run docker container image. This should launch an interactive menu through
which you can controll your agents wallets & communication with market platform.


```shell
$ docker-compose run --rm app python run_menu.py
```


Alternatively, **if you are using the pre-built docker containers**, use the production Compose file:

```shell
$ docker-compose -f docker-compose.prod.yml run --rm app python run_menu.py
```
