import unittest
import json
import os
from pathlib import Path
from iiifManifest import iiifManifest
from MetadataMappings import MetadataMappings
from handler import get_manifest


class Test(unittest.TestCase):
    def setUp(self):
        self.ids = [
            "aspace_8177830828c061f66a16bb593fa13af1",
            "1934.007.001",
            "BPP1001_EAD",

            # "1999.024"
            # "1952.019",
            # "002097132",
            # "004862474",
            # "004476467",  # has HESB
            # "MSNCOL8501_EAD",
            # "pdf"
        ]
        self.iiif_base_url = 'iiif-manifest.test.edu'

    def test_manifest(self):
        current_path = str(Path(__file__).parent.absolute())
        for one_id in self.ids:
            # print("id = ", one_id)
            standard_json_file_name = os.path.join(current_path, 'test', one_id + '.standard.json')
            with open(standard_json_file_name, 'r') as input_source:
                standard_json = json.load(input_source)
            manifest_json = get_manifest(one_id, standard_json, self.iiif_base_url)
            manifest_json_file_name = os.path.join(current_path, 'test', one_id + '.manifest.json')
            # with open(os.path.join(current_path, 'test', one_id + '.actual.manifest.json'), 'w') as output_file:
            #     json.dump(manifest_json, output_file, indent=2)
            # with open(manifest_json_file_name, 'w') as output_file:
            #     json.dump(manifest_json, output_file, indent=2)
            with open(manifest_json_file_name, 'r') as input_source:
                expected_results = json.load(input_source)
            self.assertEqual(manifest_json, expected_results)

    # def test_manifest_that_is_a_pdf_without_a_mime_type(self):
    #     data = load_data_for_test('pdf')
    #     # remove the mime type
    #     parent = load_standard_json('pdf', config)
    #     parent.object['items'][0]['mimeType'] = ''

    #     mapping = MetadataMappings(parent)
    #     iiif = iiifManifest(config, parent, mapping)
    #     manifest = iiif.manifest()
    #     # debug_json(data['manifest_json'], manifest)
    #     manifest_json = "".join(json.dumps(data['manifest_json'], sort_keys=True).split())
    #     result_json = "".join(json.dumps(manifest, sort_keys=True).split())
    #     self.assertEqual(result_json, manifest_json)

    # def test_addProvider(self):
    #     tests = [
    #         {"provider": "rare", "result": "https://rarebooks.library.nd.edu/using"},
    #         {"provider": "hesb", "result": "https://library.nd.edu"},
    #         {"provider": "museum", "result": "https://sniteartmuseum.nd.edu/about-us/contact-us/"},
    #         {"provider": "unda", "result": "http://archives.nd.edu/about/"}
    #     ]

    #     # parent = load_csv_data("item-one-image-embark", config)
    #     parent = load_standard_json("item-one-image-embark", config)
    #     # print("parent = ", parent)
    #     for test in tests:
    #         parent.object['repository'] = test.get("provider")
    #         mapping = MetadataMappings(parent)
    #         iiif = iiifManifest(config, parent, mapping)
    #         iiif.add_provider()
    #         self.assertEqual(test.get("result"), iiif.manifest_hash['provider'][0].get('id'))

    #     # if there is no repository there is no result
    #     del parent.object['repository']
    #     mapping = MetadataMappings(parent)
    #     iiif = iiifManifest(config, parent, mapping)
    #     iiif.add_provider()
    #     self.assertEqual("not here", iiif.manifest_hash.get('provider', "not here"))
    #     # reset
    #     parent.object['repository'] = 'rbsc'

    #     # if the type is file we don't show anything either.
    #     parent.object['level'] = 'file'
    #     mapping = MetadataMappings(parent)
    #     iiif = iiifManifest(config, parent, mapping)
    #     iiif.add_provider()
    #     self.assertEqual("not here", iiif.manifest_hash.get('provider', "not here"))
    #     # reset
    #     parent.object['level'] = 'collection'

    # def test_metadata_mappings(self):
    #     # it converts floats to strings
    #     # parent = load_csv_data("item-one-image-embark", config)
    #     parent = load_standard_json("item-one-image-embark", config)
    #     parent.object["uniqueIdentifier"] = 1999.2312

    #     mapping = MetadataMappings(parent)
    #     iiif = iiifManifest(config, parent, mapping)
    #     iiif.metadata_array()
    #     self.assertEqual("1999.2312", iiif.manifest_hash.get("metadata")[4].get("value").get("en")[0])


def suite():
    """ define test suite """
    return unittest.TestLoader().loadTestsFromTestCase(Test)


if __name__ == '__main__':
    suite()
    unittest.main()
