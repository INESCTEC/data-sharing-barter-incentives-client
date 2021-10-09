#!/usr/bin/env bash

docker build -f Dockerfile -t docker-registry.inesctec.pt/valorem/valorem-client-python/valorem-client-python-app .
docker push docker-registry.inesctec.pt/valorem/valorem-client-python/valorem-client-python-app
