#!/usr/bin/env bash

if [ "$1" = "-t" ] || [ "$1" = "--test" ]; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
    echo -ne "Would you like to publish to PyPI [y/n]? "
    read -r -n1 publish
    if [[ "$publish" =~ [Yy] ]]; then
        twine upload dist/*
        echo
        echo "Published"
    else
        echo
        echo "Exiting"
    fi
fi

