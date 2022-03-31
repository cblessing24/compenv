#!/bin/sh

if [ -f /root/setup.sh ]; then
    /root/setup.sh && pdm run "$@"
else
    pdm run "$@"
fi
