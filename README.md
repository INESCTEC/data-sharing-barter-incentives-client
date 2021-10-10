# valorem-client-python

Python client for VALOREM project 

**Warning: This package should be used exclusively for tests / debug purposes.**

## Install:

First, build docker container image: 

    > docker-compose build


Alternatively, you can also download the docker container from INESC TEC Gitlab Registry


* Login into inesctec registry:

    > docker login docker-registry.inesctec.pt


* Pull pre-built container image from registry:

    > docker-compose -f docker-compose.prod.yml pull

## Usage:

Second, run docker container image. This should launch an interactive menu through
which you can controll your agents wallets & communication with market platform.

    > docker-compose run --rm app python run_menu.py

    OR, if you are using the pre-built docker containers:

    > docker-compose -f docker-compose.prod.yml run --rm app python run_menu.py