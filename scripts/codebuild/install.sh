#!/bin/bash
echo "[Install phase] `date` in `pwd`"

# install dependencies for specific lambdas

pushd manifest_lambda
./local_install.sh
popd

