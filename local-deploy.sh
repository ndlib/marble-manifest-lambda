#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "REQUIRED: stack name"
    echo "USAGE: local-deploy.sh <stackname>"
    exit 1
fi

# grab the latest linter
template_linter_path="https://raw.githubusercontent.com/ndlib/py-template/master/"
template_linter_file=".flake8"
template_linter=${template_linter_path}${template_linter_file}

curl ${template_linter} -o ${template_linter_file} -s

# install dev pkgs
dev_req="dev-requirements.txt"
if test -f "${dev_req}"; then
    pip install -r ${dev_req}
fi

# prep deploy
stackname=${1}
deploy_cfg="deploy.json"
stack_json="{ \"stackname\": \"${stackname}\" }"
echo ${stack_json} > ${deploy_cfg}

# deploy
cdk deploy