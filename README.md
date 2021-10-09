# valorem-client-python

Python client for VALOREM project 

**Warning: This package should be used exclusively for tests / debug purposes.**

## Install:

First, build docker container image: 

    > docker-compose build

Alternatively, you can also download the docker container from INESC TEC Gitlab Registry

## Usage:

Second, run docker container image. This should launch an interactive menu through
which you can controll your agents wallets & communication with market platform.

    > docker-compose run --rm app python run_menu.py

