import _set_path  # noqa
import boto3
import botocore
import os
from iiifManifest import iiifManifest
from MetadataMappings import MetadataMappings
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from graphql import query_appsync, build_manifest_query, build_file_query
import json


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[AwsLambdaIntegration()]
    )


def run(event, context):
    graphql_url = _get_ssm_parameter(os.environ.get('GRAPHQL_API_URL_KEY_PATH'))
    graphql_key = _get_ssm_parameter(os.environ.get('GRAPHQL_API_KEY_KEY_PATH'))
    iiif_base_url = os.environ.get('IIIF_API_BASE_URL', '')
    resource = event.get('resource', "").replace("{id}", "").replace("/", "")
    id = event.get("pathParameters", {}).get("id", "").replace("%2F", "/")
    manifest_json = {}

    if graphql_url and graphql_key and iiif_base_url and resource and id:
        try:
            if resource == 'manifest':
                print("manifest_query = ", build_manifest_query(id))
                standard_json = query_appsync(graphql_url, graphql_key, build_manifest_query(id)).get('data', {}).get('getItem')
                print("standard_json =", standard_json)
                with open(id + '.standard.json', 'w') as output_file:
                    json.dump(standard_json, output_file, indent=2)
                manifest_json = get_manifest(id, standard_json, iiif_base_url)
            elif resource in ('canvas', 'annotation_page', 'annotation'):  # This assumes the canvas is named with the full file id, including extension
                standard_json = query_appsync(graphql_url, graphql_key, build_file_query(id)).get('data', {}).get('getFile')
                manifest_json = get_manifest(id, standard_json, iiif_base_url)
                if resource in ('annotation_page', 'annotation'):  # This assumes one annotation_page per canvas
                    manifest_json = manifest_json.get('items')[0]
                    if resource in ('annotation'):  # This assumes one annotation per annoation_page
                        manifest_json = manifest_json.get('items')[0]
        except Exception as err:
            print("error on {}".format(id))
            print("Error: {}".format(err))
            manifest_json = {}
    else:
        print("graphql_url =", graphql_url)
        print("resource =", resource)
        print("id =", id)

    # with open('manifest.json', 'w') as output_file:
    #     json.dump(manifest_json, output_file, indent=2)

    return build_http_results(manifest_json)


def build_http_results(manifest_json: dict) -> dict:
    status_code = 200
    if not manifest_json:
        status_code = 400
    return {
        "headers": {'Access-Control-Allow-Origin': '*'},
        "statusCode": status_code,
        "body": json.dumps(manifest_json)
    }


def get_manifest(id: str, standard_json: dict, iiif_base_url: str):
    manifest = {}
    if standard_json and iiif_base_url:
        mapping_template = MetadataMappings(standard_json.get('sourceSystem', 'aleph')).standard_json_mapping
        iiif = iiifManifest(iiif_base_url, standard_json, mapping_template)
        manifest = iiif.manifest()
    return manifest


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


# python -c 'from handler import *; test()'

# export GRAPHQL_API_URL_KEY_PATH=/all/stacks/steve-maintain-metadata/graphql-api-url
# export GRAPHQL_API_KEY_KEY_PATH=/all/stacks/steve-maintain-metadata/graphql-api-key
# export IIIF_API_BASE_URL=presentation-iiif.library.nd.edu
# aws-vault exec testlibnd-superAdmin


# export GRAPHQL_API_URL_KEY_PATH=/all/stacks/marbleb-prod-maintain-metadata/graphql-api-url
# export GRAPHQL_API_KEY_KEY_PATH=/all/stacks/marbleb-prod-maintain-metadata/graphql-api-key
# export IIIF_API_BASE_URL=presentation-iiif.library.nd.edu
# aws-valut exec libnd-power-user-2
# python -c 'from handler import *; test()'

def test():
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    event = {}
    event['resource'] = '/manifest/{id}'
    event['pathParameters'] = {"id": "BPP1001_EAD"}
    # event['id'] = 'MSNEa8006_EAD'
    # event['id'] = '1934.007.001'
    # event['id'] = 'aspace_8177830828c061f66a16bb593fa13af1'

    # event['resource'] = 'canvas'
    # event['resource'] = 'annotation_page'
    # event['resource'] = 'annotation'
    # event['id'] = '1934.007.001/1934_007_001-v0002.tif'

    print(run(event, {}))
