#!/bin/bash

mkdir -p reports \
    && chmod 777 reports \
    && docker build -t compenv . \
    && docker network create test \
    && docker run \
        --rm \
        -v "$PWD/reports:/home/dev/reports" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -u dev:"$(stat -c "%g" /var/run/docker.sock)" \
        -e DOCKER=1 \
        --net test \
        compenv pytest --cov --cov-report=xml:/home/dev/reports/coverage.xml \
    && bash <(curl -s https://codecov.io/bash) -f "$PWD/reports/coverage.xml"
