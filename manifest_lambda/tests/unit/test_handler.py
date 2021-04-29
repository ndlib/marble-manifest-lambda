import unittest
import json
import os
from pathlib import Path
from manifest_lambda.handler import get_manifest, _get_graphql_api_url_key_path, _get_graphql_api_key_key_path, _get_iiif_api_base_url, \
    _get_resource, _get_id


class Test(unittest.TestCase):
    def setUp(self):
        self.ids = [
            "aspace_8177830828c061f66a16bb593fa13af1",
            "1934.007.001",
            "BPP1001_EAD",
        ]
        self.iiif_base_url = 'iiif-manifest.test.edu'

    def test_get_graphql_api_url_key_path(self):
        expected_results = '/all/stacks/api/key/path'
        os.environ['GRAPHQL_API_URL_KEY_PATH'] = expected_results
        actual_results = _get_graphql_api_url_key_path()
        self.assertEqual(actual_results, expected_results)

    def test_get_graphql_api_key_key_path(self):
        expected_results = '/all/stacks/key/key/path'
        os.environ['GRAPHQL_API_KEY_KEY_PATH'] = expected_results
        actual_results = _get_graphql_api_key_key_path()
        self.assertEqual(actual_results, expected_results)

    def test_get_iiif_api_base_url(self):
        expected_results = 'http://my.iiif.api.base.url'
        os.environ['IIIF_API_BASE_URL'] = expected_results
        actual_results = _get_iiif_api_base_url()
        self.assertEqual(actual_results, expected_results)

    def test_get_resource(self):
        expected_results = 'manifest'
        event = {"resource": "/manifest/{id}"}
        actual_results = _get_resource(event)
        self.assertEqual(actual_results, expected_results)

    def test_get_id(self):
        expected_results = 'MSNEa8006_EAD/aspace_198bcdd50f073d154c057eed07807f8f'
        event = {"pathParameters": {"id": "MSNEa8006_EAD%2Faspace_198bcdd50f073d154c057eed07807f8f"}}
        actual_results = _get_id(event)
        self.assertEqual(actual_results, expected_results)

    def test_manifest(self):
        current_path = str(Path(__file__).parent.absolute())
        for one_id in self.ids:
            # print("id = ", one_id)
            standard_json_file_name = os.path.join(current_path, '..', one_id + '.standard.json')
            with open(standard_json_file_name, 'r') as input_source:
                standard_json = json.load(input_source)
            manifest_json = get_manifest(one_id, standard_json, self.iiif_base_url)
            manifest_json_file_name = os.path.join(current_path, '..', one_id + '.manifest.json')
            # with open(manifest_json_file_name, 'w') as output_file:
            #     json.dump(manifest_json, output_file, indent=2)
            with open(manifest_json_file_name, 'r') as input_source:
                expected_results = json.load(input_source)
            self.assertEqual(manifest_json, expected_results)


def suite():
    """ define test suite """
    return unittest.TestLoader().loadTestsFromTestCase(Test)


if __name__ == '__main__':
    suite()
    unittest.main()
