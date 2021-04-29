import unittest
import json
import os
from pathlib import Path
from manifest_lambda.MetadataMappings import MetadataMappings


current_path = str(Path(__file__).parent.absolute())


class Test(unittest.TestCase):
    def test_load_source_system_mapping_file(self):
        """ test_load_source_system_mapping_file """
        site_name = 'marble'
        for source_system in ['aleph', 'archivesspace', 'curate', 'embark']:
            file_name = os.path.join(current_path, '../../sites', site_name, source_system + '.json')
            with open(file_name, 'r') as input_source:
                expected_results = json.load(input_source)
            metadata_mappings_class = MetadataMappings(source_system)
            actual_results = metadata_mappings_class.load_json_file(site_name, source_system)
            self.assertEqual(actual_results, expected_results)

    def test_loadMetadataRules(self):
        """ test_loadMetadataRules """
        metadata_mappings_class = MetadataMappings('aleph')
        mapping_rules = metadata_mappings_class.loadMetadataRules()
        actual_results = mapping_rules.get('title', {}).get('marble_title')
        expected_results = 'Title'
        self.assertEqual(actual_results, expected_results)


def suite():
    """ define test suite """
    return unittest.TestLoader().loadTestsFromTestCase(Test)


if __name__ == '__main__':
    suite()
    unittest.main()
