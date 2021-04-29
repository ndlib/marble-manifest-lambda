#!/bin/bash
echo "[Install phase] `date` in `pwd`"

# install dependencies for specific lambdas

pushd manifest_lambda
rm -rf ./dependencies
mkdir dependencies
pip install -r requirements.txt -t ./dependencies
popd

