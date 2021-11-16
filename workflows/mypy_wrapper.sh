#!/bin/bash

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

output=$(mypy | head -n -1 | grep -v -x -E -f "$script_dir"/mypy_ignored.txt)
printf "$output"

if [ $(printf "$output" | wc -l) -ne 0 ]; then
    exit 1;
fi
