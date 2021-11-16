#!/bin/bash

linters=('black --check --diff .' 'isort --check --diff .' 'flake8 .' 'workflows/mypy_wrapper.sh' 'pylint repro')

echo 'Building Docker image...'
docker build -t reproducibility . || exit 1

exit_code=0
for linter in "${linters[@]}"
do
    echo "Checking code with '$linter'..."
    if ! eval "docker run reproducibility $linter";
    then
        exit_code=1
    fi
done
exit "$exit_code"
