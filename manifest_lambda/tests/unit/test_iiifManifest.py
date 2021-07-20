import unittest
import json
import os
from pathlib import Path
from manifest_lambda.iiifManifest import iiifManifest, _metadata_keys_that_have_top_level_values, _search_for_default_image, _annotation_page_id, \
    _lang_wrapper, _convert_label_value, \
    _return_part_of, _return_required_statement, _return_rights, _return_summary
from manifest_lambda.MetadataMappings import MetadataMappings
from manifest_lambda.get_iiif_manifest_provider import _hesb_proivider, _archives_proivider, _rbsc_proivider, _snite_proivider, return_provider

current_path = str(Path(__file__).parent.absolute())

media_extensions_list = ['.mp3', '.mp4', '.pdf', '.wav']


class Test(unittest.TestCase):
    def setUp(self):
        self.standard_json = {}
        file_name = os.path.join(current_path, '..', '1934.007.001.standard.json')
        with open(file_name, 'r') as input_source:
            self.standard_json = json.load(input_source)
        self.iiif_base_url = 'https://my.base.url'
        self.mapping_template = MetadataMappings(self.standard_json.get('sourceSystem', 'aleph')).standard_json_mapping
        self.iiif_manifest_class = iiifManifest(self.iiif_base_url, self.standard_json, self.mapping_template, media_extensions_list)

    def test_metadata_keys_that_have_top_level_values(self):
        """ test_metadata_keys_that_have_top_level_values """
        actual_results = _metadata_keys_that_have_top_level_values()
        expected_results = [
            'title',
            'provider',
            'creator',
            'description',
            'collectioninformation',
            'repository',
            'copyrightStatus',
            # 'copyrightStatement',
            'usage',
            'license',
            'thumbnail',
        ]
        self.assertEqual(actual_results, expected_results)

    def test_search_for_default_image(self):
        "test_search_for_default_image"
        actual_results = _search_for_default_image(self.standard_json)
        expected_results = {
            'id': '1934.007.001/1934_007_001-v0003.tif',
            'level': 'file',
            'mediaResourceId': '1934.007.001%2F1934_007_001-v0003',
            'mediaServer': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2'
        }
        self.assertEqual(actual_results, expected_results)

    def test_annotation_page_id(self):
        """ test_annotation_page_id """
        actual_results = _annotation_page_id(self.iiif_base_url, "my_item_id")
        expected_results = "https://my.base.url/annotation_page/my_item_id"
        self.assertEqual(actual_results, expected_results)

    def test_hesb_provider(self):
        """ test_hesb_provider """
        actual_id = _hesb_proivider().get('id')
        expected_id = 'https://library.nd.edu'
        self.assertEqual(actual_id, expected_id)

    def test_archives_proivider(self):
        """ test_archives_proivider """
        actual_id = _archives_proivider().get('id')
        expected_id = 'http://archives.nd.edu/about/'
        self.assertEqual(actual_id, expected_id)

    def test_rbsc_proivider(self):
        """ test_rbsc_proivider """
        actual_id = _rbsc_proivider().get('id')
        expected_id = 'https://rarebooks.library.nd.edu/using'
        self.assertEqual(actual_id, expected_id)

    def test_snite_proivider(self):
        """ test_snite_proivider """
        actual_id = _snite_proivider().get('id')
        expected_id = 'https://sniteartmuseum.nd.edu/about-us/contact-us/'
        self.assertEqual(actual_id, expected_id)

    def test_lang_wrapper(self):
        """ test_lang_wrapper """
        actual_results = _lang_wrapper('lang', 'some_line')
        expected_results = {'lang': ['some_line']}
        self.assertEqual(actual_results, expected_results)

    def test_convert_label_value(self):
        """ test_convert_label_value """
        actual_results = _convert_label_value('lang', 'my_label', 'my_value')
        expected_results = {'label': {'lang': ['my_label']}, 'value': {'lang': ['my_value']}}
        self.assertEqual(actual_results, expected_results)

    def test_return_provider(self):
        """ test_return_provider """
        results = return_provider(self.standard_json.get('repository'), self.standard_json.get('level', 'file'))
        actual_id = results.get('id')
        expected_id = 'https://sniteartmuseum.nd.edu/about-us/contact-us/'
        self.assertEqual(actual_id, expected_id)

    def test_return_part_of(self):
        """ test_return_part_of """
        actual_results = _return_part_of('Manifest', 'parent_id', 'collection', 'http://iiif.base.url')
        expected_results = {'id': 'http://iiif.base.url/manifest/parent_id', 'type': 'Collection'}
        self.assertEqual(actual_results, expected_results)
        actual_results = _return_part_of('Manifest', 'parent_id', 'manifest', 'http://iiif.base.url')
        expected_results = {'id': 'http://iiif.base.url/manifest/parent_id', 'type': 'Manifest'}
        self.assertEqual(actual_results, expected_results)
        actual_results = _return_part_of('Manifest', 'root', 'manifest', 'http://iiif.base.url')
        expected_results = {}
        self.assertEqual(actual_results, expected_results)

    def test_return_required_statement(self):
        """ test_return_required_statement """
        actual_results = _return_required_statement('my_lang', 'my copyright status')
        expected_results = {'label': {'my_lang': ['Copyright']}, 'value': {'my_lang': ['my copyright status']}}
        self.assertEqual(actual_results, expected_results)

    def test_return_rights(self):
        """ test_return_rights """
        actual_results = _return_rights('my copyright statement')
        expected_results = 'my copyright statement'
        self.assertEqual(actual_results, expected_results)
        actual_results = _return_rights('')
        self.assertFalse(actual_results)

    def test_return_summary(self):
        """ test_return_summary """
        actual_results = _return_summary('my_lang', 'my description')
        expected_results = {'my_lang': ['my description']}
        self.assertEqual(actual_results, expected_results)


def suite():
    """ define test suite """
    return unittest.TestLoader().loadTestsFromTestCase(Test)


if __name__ == '__main__':
    suite()
    unittest.main()
