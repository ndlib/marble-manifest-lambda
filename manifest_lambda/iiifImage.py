import os


class iiifImage():
    def __init__(self, standard_json: dict, iiif_base_url: str, media_extensions_list: list):
        self.iiif_base_url = iiif_base_url
        self.standard_json = standard_json
        self.media_extensions_list = media_extensions_list

    def thumbnail(self, width="250", height="") -> dict:
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
        mime_type = self.standard_json.get('mimeType', '')
        if 'pdf' in mime_type or 'audio' in mime_type or 'video' in mime_type:
            return False
        if self._does_path_have_media_extension(self.standard_json.get('id', '')):
            print("id has media extension")
            return False
        if self._does_path_have_media_extension(self.standard_json.get('defaultFilePath', '')):
            return False
        if self._does_path_have_media_extension(self.standard_json.get('defaultImage', {}.get('id', ''))):
            return False
        return True

    def _does_path_have_media_extension(self, field_to_test: str) -> bool:
        _file_name, file_extension = os.path.splitext(field_to_test)
        if file_extension.lower() in self.media_extensions_list:
            return True
        return False

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
