# MARBLE-related
# Archived 2023-05-12 sm

# Marble Manifest Lambda

## This creates a lambda that will create pieces of a iiif Manifest on-the-fly from metadata stored in AppSync

## Installation

1. Setup pyenv - <https://github.com/pyenv/pyenv>
2. Setup aws-cdk - <https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html>

Use venv - <https://docs.python.org/3/library/venv.html>

venv is included in the Python standard library and requires no additional installation. Additional details in deployment.

## Testing

Use unittest - <https://docs.python.org/3/library/unittest.html>

Tests should be placed in manifest_lambda/tests/unit

To execute all test: `python run_all_tests.py`

## Dependencies

### Development Dependencies

Review the dev-requirements.txt to update development packages
An example would be our linter package - flake8

### Production Dependencies

Review the install_requires in setup.py to update production packages

## Deployment

### Local deployment to AWS

1. Setup virtual env
    1. python -m venv .env
    2. source .env/bin/activate
2. Run local deployment
    1. local-deploy.sh mystackname
3. Exit virtual env
    1. deactivate
