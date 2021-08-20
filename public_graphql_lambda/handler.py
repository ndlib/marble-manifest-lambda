import _set_path  # noqa
import boto3
import botocore
import os
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
import json
from urllib import request, error


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[AwsLambdaIntegration()]
    )


def run(event, context):
    status_code = 200  # default to Success
    results_json = {}

    graphql_url = _get_ssm_parameter(_get_graphql_api_url_key_path())
    graphql_key = _get_ssm_parameter(_get_graphql_api_key_key_path())

    id = _get_id(event)
    if id not in ['listPublicPortfolioCollections', 'listHighlightedPortfolioCollections', 'listPublicFeaturedPortfolioCollections', 'getPortfolioCollection', 'getPortfolioUser']:
        status_code = 405  # Method not found
    query = event.get('body')
    if graphql_url and graphql_key and id and query:
        try:
            results_json = query_appsync(graphql_url, graphql_key, query)
        except Exception as err:
            print("error on {}".format(id))
            print("Error: {}".format(err))
            results_json = {}
    else:
        print("unable to call AppSync, we're missing key information.")
        print("graphql_url =", graphql_url)
        print("id =", id)
        if not graphql_key:
            print("missing graphql_key")

    # if results_json:
    #     with open('results_json.json', 'w') as output_file:
    #         json.dump(results_json, output_file, indent=2)
    print("got to res", results_json)

    return build_http_results(results_json, status_code)


def _get_graphql_api_url_key_path() -> str:
    return os.environ.get('GRAPHQL_API_URL_KEY_PATH')


def _get_graphql_api_key_key_path() -> str:
    return os.environ.get('GRAPHQL_API_KEY_KEY_PATH')


def _get_resource(event: dict) -> str:
    return event.get('resource', "").replace("{id}", "").replace("/", "")


def _get_id(event: dict) -> str:
    # print("pathParamters = ", event.get("pathParameters"))
    return event.get("pathParameters", {}).get("id", "")


def build_http_results(results_json: dict, status_code: int) -> dict:
    if status_code == 200 and not results_json:
        status_code = 400  # Bad Request
    if status_code != 200:
        results_json = {}  # Blank out results if all is not well.
    return {
        "headers": {'Access-Control-Allow-Origin': '*'},
        "statusCode": status_code,
        "body": json.dumps(results_json)
    }


def _get_ssm_parameter(name: str) -> str:
    if not name:
        return None
    try:
        response = boto3.client('ssm').get_parameter(Name=name, WithDecryption=True)
        value = response.get('Parameter').get('Value')
        return value
    except botocore.exceptions.ClientError:
        print("can't read ssm parameter: ", name)
        return None


def query_appsync(graphql_api_url: str, graphql_api_key: str, query: str):
    r = request.Request(
        headers={"x-api-key": graphql_api_key},
        url=graphql_api_url,
        method="POST",
        data=query.encode("utf8")
    )
    try:
        response = request.urlopen(r).read()
        return json.loads(response.decode("utf8"))
    except error.URLError as ue:
        print("error:", ue)
        return {}


# python -c 'from handler import *; test()'

# export GRAPHQL_API_URL_KEY_PATH=/all/stacks/steve-maintain-metadata/graphql-api-url
# export GRAPHQL_API_KEY_KEY_PATH=/all/stacks/steve-maintain-metadata/graphql-api-key
# aws-vault exec testlibnd-superAdmin


# export GRAPHQL_API_URL_KEY_PATH=/all/stacks/marbleb-prod-maintain-metadata/graphql-api-url
# export GRAPHQL_API_KEY_KEY_PATH=/all/stacks/marbleb-prod-maintain-metadata/graphql-api-key
# python -c 'from handler import *; test()'


def test():
    event = {}
    event['resource'] = '/query/{id}'
    event['pathParameters'] = {"id": "listPublicFeaturedPortfolioCollections"}
    event['body'] = '''query MyQuery {
        listPublicFeaturedPortfolioCollections {
            items {
                portfolioUserId
                portfolioCollectionId
                description
                featuredCollection
                highlightedCollection
                layout
                imageUri
                privacy
            }
        }
    }'''

    event['body'] = '''listPublicFeaturedPortfolioCollections {
            items {
                portfolioUserId
                portfolioCollectionId
                description
                featuredCollection
                highlightedCollection
                layout
                imageUri
                privacy
            }
        }'''
    results = run(event, {})
    print("results =", results)
