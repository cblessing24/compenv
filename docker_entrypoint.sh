#!/bin/sh

"$ENTRYPOINT_DIR"/setup.sh && pdm run nvim "$@"
