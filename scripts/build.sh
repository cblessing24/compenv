#!/bin/sh

build_base_image() {
    ref=$(git rev-parse HEAD)
    docker build --build-arg COMPENV_REF="$ref" -t cblessing24/compenv:latest .
}

build_dev_image() {
    ref=$(git ls-remote https://github.com/cblessing24/dotfiles main | cut -d '	' -f 1)
    docker build \
        --build-arg UID="$(id -u)" \
        --build-arg GID="$(id -g)" \
        --build-arg BASE=cblessing24/compenv:latest \
        --build-arg DOTFILES_REF="$ref" \
        -f Dockerfile.dev \
        -t compenv_dev .
}

case "$1" in
    all)
        build_base_image
        build_dev_image
        ;;
    base)
        build_base_image
        ;;
    dev)
        build_dev_image
        ;;
    *)
        echo "Usage: $0 {all|base|dev}"
        exit 1
esac
