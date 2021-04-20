#!/usr/bin/env python
import json
import os

from aws_cdk import core

from deploy.deploy_stack import DeployStack

# generated from local-deploy.sh
cfg = "deploy.json"
stackname = None
if os.path.exists(cfg):
    with open(cfg) as deploy_cfg:
        stackname = json.load(deploy_cfg)["stackname"]

# use user generated stackname or create one
if stackname is None:
    homedir = os.path.expanduser("~")  # /home/<username>
    cwd = os.getcwd()  # /my/path/to/projects
    owner = os.path.basename(os.path.normpath(homedir))
    project = os.path.basename(os.path.normpath(cwd))
    stackname = owner + "_" + project  # username_project

# run it!
app = core.App()
DeployStack(app, stackname)

app.synth()
