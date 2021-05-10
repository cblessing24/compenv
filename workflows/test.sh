#!/bin/bash

mkdir -p reports \
    && chmod 777 reports \
    && docker build -t reproducibility . \
    && docker run -v "$PWD/reports:/home/dev/reports" reproducibility pytest --cov --cov-report=xml:/home/dev/reports/coverage.xml tests \
    && bash <(curl -s https://codecov.io/bash) -f "$PWD/reports/coverage.xml"
