import unittest
import json
import os
from pathlib import Path
from iiifImage import iiifImage


current_path = str(Path(__file__).parent.absolute())

media_extensions_list = ['.mp3', '.mp4', '.pdf', '.wav']


class Test(unittest.TestCase):
    def setUp(self):
        self.example_standard_json = {}
        file_name = os.path.join(current_path, '..', '1934.007.001.standard.json')
        with open(file_name, 'r') as input_source:
            self.example_standard_json = json.load(input_source)
        self.iiif_base_url = 'https://my.base.url'

    def test_is_image(self):
        """ test_is_image """
        sample_files_json = {
            "id": "1934.007.001/1934_007_001-v0003.tif",
            "mediaResourceId": "1934.007.001%2F1934_007_001-v0003",
            "mediaServer": "https://image-iiif-testlib.libraries.nd.edu/iiif/2"
        }
        iiif_image_class = iiifImage(sample_files_json, self.iiif_base_url, media_extensions_list)
        self.assertTrue(iiif_image_class.is_image())

    def test_is_image_pdf(self):
        """ test_is_image_pdf """
        sample_files_json = {
            "id": "1934.007.001/1934_007_001-v0003.pdf",
            "mediaResourceId": "1934.007.001%2F1934_007_001-v0003",
            "mediaServer": "https://image-iiif-testlib.libraries.nd.edu/iiif/2"
        }
        iiif_image_class = iiifImage(sample_files_json, self.iiif_base_url, media_extensions_list)
        self.assertFalse(iiif_image_class.is_image())

    def test_is_image_mimeType(self):
        """ test_is_image_mimeType """
        sample_files_json = {
            "id": "1934.007.001/1934_007_001-v0003.tif",
            "mediaResourceId": "1934.007.001%2F1934_007_001-v0003",
            "mediaServer": "https://image-iiif-testlib.libraries.nd.edu/iiif/2",
            "mimeType": "application/pdf"
        }
        iiif_image_class = iiifImage(sample_files_json, self.iiif_base_url, media_extensions_list)
        self.assertFalse(iiif_image_class.is_image())

    def test_other_things(self):
        """ test_other_things """
        sample_files_json = {
            "id": "1934.007.001/1934_007_001-v0003.tif",
            "mediaResourceId": "1934.007.001%2F1934_007_001-v0003",
            "mediaServer": "https://image-iiif-testlib.libraries.nd.edu/iiif/2"
        }
        iiif_image_class = iiifImage(sample_files_json, self.iiif_base_url, media_extensions_list)
        actual_thumbnail_results = iiif_image_class.thumbnail()
        expected_thumbnail_results = {
            'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003/full/250,/0/default.jpg',
            'type': 'Image',
            'service': [
                {'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003', 'type': 'ImageService2', 'profile': 'http://iiif.io/api/image/2/level2.json'}
            ]
        }
        self.assertEqual(expected_thumbnail_results, actual_thumbnail_results)
        actual_annotation_id = iiif_image_class._annotation_id()
        expected_annotation_id = 'https://my.base.url/annotation/1934.007.001%2F1934_007_001-v0003.tif'
        self.assertEqual(actual_annotation_id, expected_annotation_id)
        actual_image_url_id = iiif_image_class._image_url_id()
        expected_image_url_id = 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003'
        self.assertEqual(actual_image_url_id, expected_image_url_id)
        actual_service = iiif_image_class._service()
        expected_service = {
            'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003',
            'profile': 'http://iiif.io/api/image/2/level2.json',
            'type': 'ImageService2'
        }
        self.assertEqual(actual_service, expected_service)
        actual_image = iiif_image_class.image()
        expected_image = {
            'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003/full/full/0/default.jpg',
            'type': 'Image',
            'format': 'image/jpeg',
            'service': [
                {
                    'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003',
                    'type': 'ImageService2',
                    'profile': 'http://iiif.io/api/image/2/level2.json'
                }
            ]
        }
        self.assertTrue(actual_image, expected_image)
        actual_annotation = iiif_image_class.annotation('my_canvas_url_id')
        expected_annotation = {
            'body': {
                'format': 'image/jpeg',
                'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003/full/full/0/default.jpg',
                'service': [
                    {
                        'id': 'https://image-iiif-testlib.libraries.nd.edu/iiif/2/1934.007.001%2F1934_007_001-v0003',
                        'profile': 'http://iiif.io/api/image/2/level2.json',
                        'type': 'ImageService2'
                    }
                ],
                'type': 'Image'
            },
            'id': 'https://my.base.url/annotation/1934.007.001%2F1934_007_001-v0003.tif',
            'motivation': 'painting',
            'target': 'my_canvas_url_id',
            'type': 'Annotation'
        }
        self.assertEqual(actual_annotation, expected_annotation)


def suite():
    """ define test suite """
    return unittest.TestLoader().loadTestsFromTestCase(Test)


if __name__ == '__main__':
    suite()
    unittest.main()
