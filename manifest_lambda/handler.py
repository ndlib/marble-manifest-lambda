import _set_path  # noqa
import boto3
import botocore
import os
from iiifManifest import iiifManifest
from MetadataMappings import MetadataMappings
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from graphql import query_appsync, build_manifest_query, build_image_query, build_media_query
import json


if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[AwsLambdaIntegration()]
    )


def run(event, context):  # noqa: C901
    graphql_url = _get_ssm_parameter(_get_graphql_api_url_key_path())
    graphql_key = _get_ssm_parameter(_get_graphql_api_key_key_path())
    iiif_base_url = _get_iiif_api_base_url()
    resource = _get_resource(event)
    id = _get_id(event)
    manifest_json = {}
    media_extensions_list = ['.mp3', '.mp4', '.pdf', '.wav']

    if graphql_url and graphql_key and iiif_base_url and resource and id:
        try:
            if resource == 'manifest':
                standard_json = query_appsync(graphql_url, graphql_key, build_manifest_query(id)).get('data', {}).get('getItem')
                if standard_json.get('id') is None:
                    standard_json = {}
                manifest_json = get_manifest(id, standard_json, iiif_base_url, media_extensions_list)
            elif resource in ('canvas', 'annotation_page', 'annotation'):  # This assumes the canvas is named with the full file id, including extension
                manifest_json = get_canvas(resource, id, graphql_url, graphql_key, iiif_base_url, media_extensions_list)
        except Exception as err:
            sentry_sdk.capture_exception(err)
            print("error on {}".format(id))
            print("Error: {}".format(err))
            manifest_json = {}
    else:
        print("graphql_url =", graphql_url)
        print("resource =", resource)
        print("id =", id)

    if event.get('local', False) and event.get('saveManifestLocally', False):
        with open('manifest.json', 'w') as output_file:
            json.dump(manifest_json, output_file, indent=2)

    return build_http_results(manifest_json)


def get_canvas(resource: str, id: str, graphql_url: str, graphql_key: str, iiif_base_url: str, media_extensions_list: list) -> dict:
    manifest_json = {}
    try:
        _file_name, file_extension = os.path.splitext(id)
        if file_extension.lower() in ('.mp3', '.mp4', '.pdf', '.wav'):
            standard_json = query_appsync(graphql_url, graphql_key, build_media_query(id)).get('data', {}).get('getMedia')
        else:
            standard_json = query_appsync(graphql_url, graphql_key, build_image_query(id)).get('data', {}).get('getImage')
        if not standard_json:
            return {}
        if standard_json.get('id') is None:
            return {}
        manifest_json = get_manifest(id, standard_json, iiif_base_url, media_extensions_list)
        if resource in ('annotation_page', 'annotation'):  # This returns the first annotation_page per canvas
            manifest_json = manifest_json.get('items')[0]
            if resource in ('annotation'):  # This returns the first annotation per annoation_page
                manifest_json = manifest_json.get('items')[0]
    except Exception as err:
        sentry_sdk.capture_exception(err)
        print("error on {}".format(id))
        print("Error: {}".format(err))
        manifest_json = {}
    return manifest_json


def _get_graphql_api_url_key_path() -> str:
    return os.environ.get('GRAPHQL_API_URL_KEY_PATH')


def _get_graphql_api_key_key_path() -> str:
    return os.environ.get('GRAPHQL_API_KEY_KEY_PATH')


def _get_iiif_api_base_url() -> str:
    return os.environ.get('IIIF_API_BASE_URL', '')


def _get_resource(event: dict) -> str:
    return event.get('resource', "").replace("{id}", "").replace("/", "")


def _get_id(event: dict) -> str:
    return event.get("pathParameters", {}).get("id", "").replace("%2F", "/")


def build_http_results(manifest_json: dict) -> dict:
    status_code = 200
    if not manifest_json:
        status_code = 400
    return {
        "headers": {'Access-Control-Allow-Origin': '*'},
        "statusCode": status_code,
        "body": json.dumps(manifest_json)
    }


def get_manifest(id: str, standard_json: dict, iiif_base_url: str, media_extensions_list: str) -> dict:
    manifest = {}
    if standard_json and iiif_base_url:
        mapping_template = MetadataMappings(standard_json.get('sourceSystem', 'aleph')).standard_json_mapping
        iiif = iiifManifest(iiif_base_url, standard_json, mapping_template, media_extensions_list)
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
# aws-vault exec libnd-power-user
# python -c 'from handler import *; test()'

def test():
    event = {}
    event['local'] = True
    event['saveManifestLocally'] = True
    event['resource'] = '/manifest/{id}'
    event['pathParameters'] = {"id": "BPP1001_EAD"}
    # event['id'] = 'MSNEa8006_EAD'
    # event['id'] = '1934.007.001'
    # event['id'] = 'aspace_8177830828c061f66a16bb593fa13af1'
    # event['pathParameters']['id'] = 'pv63fx74g23'
    event['pathParameters']['id'] = 'aspace_8177830828c061f66a16bb593fa13af1'
    # event['pathParameters']['id'] = '005065260'
    # event['pathParameters']['id'] = '1934.007.001'
    event['pathParameters']['id'] = 'jm214m93b9r'

    # event['resource'] = '/canvas/{id}'
    # event['resource'] = '/annotation_page/{id}'
    # event['resource'] = '/annotation/{id}'
    # event['pathParameters'] = {"id": "public-access%2Fmedia%2FAleph%2FBOO_005065260%2FBOO_00506526001-0001.wav"}
    event['pathParameters']['id'] = '004789783'

    run(event, {})
