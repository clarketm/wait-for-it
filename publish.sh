#!/usr/bin/env bash

if [ "$1" = "-t" ] || [ "$1" = "--test" ]; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
    twine upload dist/*
fi

