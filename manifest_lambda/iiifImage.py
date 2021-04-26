import os


class iiifImage():
    def __init__(self, standard_json: dict, iiif_base_url: str):
        self.iiif_base_url = iiif_base_url
        self.standard_json = standard_json

    def thumbnail(self, width="250", height=""):
        if (self.is_image()):
            return {
                'id': self._image_url_id() + '/full/' + width + ',' + height + '/0/default.jpg',
                'type': 'Image',
                'service': [
                    self._service()
                ]
            }

        return {}

    def is_image(self):
        if self.standard_json.get('mimeType') == 'application/pdf':
            return False
        if self.standard_json.get('id', '').lower().endswith('.pdf'):
            return False
        if self.standard_json.get('defaultFilePath', '').endswith('.pdf'):
            return False
        if self.standard_json.get('defaultFile', {}).get('id', '').endswith('.pdf'):
            return False
        return True

    def annotation(self, canvas_url_id):
        return {
            'id': self._annotation_id(),
            'type': 'Annotation',
            'motivation': 'painting',
            'target': canvas_url_id,
            'body': self.image()
        }

    def image(self):
        return {
            'id': self._image_url_id() + '/full/full/0/default.jpg',
            'type': 'Image',
            'format': 'image/jpeg',
            'service': [self._service()]
        }

    def _service(self):
        return {
            'id': self._image_url_id(),
            'type': 'ImageService2',
            'profile': "http://iiif.io/api/image/2/level2.json"
        }

    def _image_url_id(self):
        return os.path.join(self.standard_json.get('mediaServer', ''), self.standard_json.get('mediaResourceId', ''))

    def _annotation_id(self):
        return os.path.join(self.iiif_base_url, 'annotation', self.standard_json.get('id', '').replace("/", "%2F"))
