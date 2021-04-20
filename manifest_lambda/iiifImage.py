import os


class iiifImage():
    def __init__(self, data, iiif_base_url: str):
        self.data = data
        self.iiif_base_url = iiif_base_url

    def thumbnail(self, width="250", height=""):
        if (self.is_image()):
            # print('data = ', self.data.object)
            return {
                'id': self._image_url_id() + '/full/' + width + ',' + height + '/0/default.jpg',
                'type': 'Image',
                'service': [
                    self._service()
                ]
            }

        return {}

    def is_image(self):
        return self.data.get('mimeType') != 'application/pdf' and os.path.splitext(self.data.get('sourceFilePath', ''))[1] != '.pdf' and os.path.splitext(self.data.get('filePath', ''))[1] != '.pdf'

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
        return os.path.join(self.data.get('mediaServer'), self.data.get('mediaResourceId'))

    def _annotation_id(self):
        return os.path.join(self.iiif_base_url, 'annotation', self.data.get('id'))
