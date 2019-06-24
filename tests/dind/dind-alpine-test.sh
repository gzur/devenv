#!/usr/bin/env sh
apk update -q && apk add -q make
export PYTHONPATH=.
make test
