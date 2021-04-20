import os
import re
from iiifImage import iiifImage


class iiifManifest():
    def __init__(self, iiif_base_url, data, mapping):
        self.iiif_base_url = iiif_base_url
        self.data = data
        self.mapping = mapping
        self.parent_id = self.data.get('collectionId')
        self.id = self.data.get('id')
        self.lang = 'en'
        self.type = self._schema_to_manifest_type()
        self.manifest_hash = {}
        self._build_mainfest()

    def manifest(self):
        return self.manifest_hash

    def key_exists(self, key):
        return key in self.data.object and self.data.get(key)

    def metadata_array(self):
        mapper = self.mapping
        keys_in_other_parts_of_manifest = self._metadata_keys_that_have_top_level_values()
        # print("self.data.object = ", self.data.object)
        ret = []
        for key in mapper.get_standard_json_keys():
            # print("key = ", key, self.data.get(key))
            if key.lower() != 'n/a':
                # print("key = ", key, " value = ", self.data.get(key, 'no value'))
                if key in ('creators', 'contributors', 'publishers', 'languages', 'subjects', 'collections'):
                    value = self.data.get(key)
                    if value:
                        # print("key, value = ", key, value)
                        value = list(map(lambda row: row.get('display', ''), value))
                # elif key == 'subjects':
                #     value = self.data.get(key, [])
                #     if value and len(value) != 0:
                #         value = list(map(lambda row: row.get('term', ''), value))
                else:
                    value = self.data.get(key, False)

                label = mapper.get_by_standard_json(key, 'marble_title')
                if label and value and key not in keys_in_other_parts_of_manifest and label.lower() != 'n/a':
                    ret.append(self._convert_label_value(label, value))

        return ret

    def thumbnail(self):
        if self.data.get('defaultFile', False):
            thumbnail = self.data.get('defaultFile')
            return [iiifImage(self.data.get('defaultFile'), self.iiif_base_url).thumbnail()]
        if self.type == 'Canvas':
            thumbnail = self.data.object
            return [iiifImage(thumbnail, self.iiif_base_url).thumbnail()]
        thumbnail = self._search_for_default_image(self.data)
        if thumbnail:
            return [iiifImage(thumbnail, self.iiif_base_url).thumbnail()]

        return []

    def _build_mainfest(self):
        label_contents = self.data.get('title')
        if not label_contents:  # file records do not have a title field
            label_contents = self.data.get('id')
        self.manifest_hash = {
            'type': self.type,
            'id': self._manifest_id(),
            'label': self._lang_wrapper(label_contents),
            'thumbnail': self.thumbnail(),
            'items': self._items(),
            'viewingDirection': 'left-to-right'
        }
        self.add_part_of()
        self.add_context()
        self.add_provider()
        self.add_required_statement()
        self.add_license()
        self.add_description()
        self.add_width_height()
        # self.add_mets()
        # self.add_schema_org()
        self.add_pdf()

        metadata = self.metadata_array()
        if len(metadata) > 0:
            self.manifest_hash['metadata'] = metadata

    def _items(self):
        ret = []
        if self.type == 'Canvas':
            image = iiifImage(self.data, self.iiif_base_url)
            ret.append({
                'id': self._annotation_page_id(),
                'type': 'AnnotationPage',
                'items': [
                    image.annotation(self._manifest_id())
                ]
            })
        else:
            for item_data in self.data.children():
                if not self.item_has_pdf(item_data):
                    ret.append(iiifManifest(self.iiif_base_url, item_data, self.mapping).manifest())
            for file_data in self.data.files_object():
                if not self.item_has_pdf(file_data):
                    ret.append(iiifManifest(self.iiif_base_url, file_data, self.mapping).manifest())

        return ret

    def _schema_to_manifest_type(self):
        if self.data.type() == 'manifest':
            return 'Manifest'
        elif self.data.type() == 'collection':
            return 'Collection'
        elif self.data.type() == 'file':
            return 'Canvas'
        elif not self.data.type():  # Note: graphql File doesn't contain a "level"
            return 'Canvas'
        raise Exception("invalid schema processor type: " + self.data.type())

    def _manifest_id(self):
        # return self.data.get('iiifUri')
        mapping = {'Collection': 'manifest', 'Manifest': 'manifest', 'Canvas': 'canvas'}
        type_of_manifest_piece = mapping.get(self.type)
        return os.path.join(self.iiif_base_url, type_of_manifest_piece, self.id)
        # return('http:/path_to_iiif_service.com/manifest/' + self.id)

    def _convert_label_value(self, label, value):
        if (label and value):
            return {
                'label': self._lang_wrapper(label),
                'value': self._lang_wrapper(value)
            }
        return None

    def _lang_wrapper(self, line):
        if type(line) != list:
            line = [line]

        line = list(map(lambda x: str(x), iter(line)))
        return {self.lang: line}

    def add_context(self):
        if self.data.root():
            self.manifest_hash["@context"] = [
                "http://www.w3.org/ns/anno.jsonld",
                "https://presentation-iiif.library.nd.edu/extensions/partiallyDigitized",
                "http://iiif.io/api/presentation/3/context.json"
            ]

    def add_part_of(self):
        if self.type == 'Manifest':
            if self.data.get('parentId') != 'root' and self.data.get('parent', {}).get('level'):
                type_of_manifest_piece = 'Manifest'
                if self.data.get('parent', {}).get('level') == 'collection':
                    type_of_manifest_piece = 'Collection'
                self.manifest_hash["partOf"] = {
                    "id": os.path.join(self.iiif_base_url, 'manifest', self.data.get('parentId')),
                    "type": type_of_manifest_piece
                }
    # def add_schema_org(self):
    #     if self.key_exists('schemaUri'):
    #         if 'seeAlso' not in self.manifest_hash:
    #             self.manifest_hash['seeAlso'] = []

    #         self.manifest_hash['seeAlso'].append({
    #             "id": self.data.get('schemaUri'),
    #             "type": "Dataset",
    #             "format": "application/ld+json",
    #             "profile": "https://schema.org/"
    #         })

    # def add_mets(self):
    #     if self.key_exists('metsUri'):
    #         if 'seeAlso' not in self.manifest_hash:
    #             self.manifest_hash['seeAlso'] = []

    #         self.manifest_hash['seeAlso'].append({
    #             "id": self.data.get('metsUri'),
    #             "type": "Dataset",
    #             "profile": "http://www.loc.gov/METS/",
    #             "format": "application/xml",
    #         })

    def add_pdf(self):
        # if we are a manifest and we have a child that is a pdf add them to a render section.
        if self.type == 'Manifest':
            pdfs = []
            for item_data in self.data.children():
                if self.item_has_pdf(item_data):
                    fileUrl = re.sub(r"^(s3:\/\/[a-zA-z_-]*?\/)", "https://rbsc.library.nd.edu/", item_data.get("filePath"))
                    pdfs.append({
                        "id": fileUrl,
                        "type": "Text",
                        "label": {"en": ["PDF Rendering"]},
                        "format": "application/pdf"
                    })

            if len(pdfs) > 0:
                self.manifest_hash['rendering'] = pdfs

    def add_width_height(self):
        if self.key_exists('height') and self.key_exists('width') and self.type == 'Canvas':
            self.manifest_hash['height'] = self.data.get('height')
            self.manifest_hash['width'] = self.data.get('width')

    def add_description(self):
        if self.key_exists('description'):
            self.manifest_hash['summary'] = self._lang_wrapper(self.data.get('description'))

    def add_license(self):
        if self.key_exists('copyrightStatement'):
            self.manifest_hash['rights'] = self.data.get('copyrightStatement')

    def add_required_statement(self):
        if self.key_exists('copyrightStatus'):
            self.manifest_hash['requiredStatement'] = self._convert_label_value('Copyright', self.data.get('copyrightStatus'))

    def add_provider(self):
        if not self.key_exists('repository'):
            return

        if self.data.type() == 'file':
            return

        provider = self.data.get('repository').lower()
        if (provider == 'museum'):
            self.manifest_hash['provider'] = [self._snite_proivider()]
        elif (provider == 'unda'):
            self.manifest_hash['provider'] = [self._archives_proivider()]
        elif (provider == 'rare' or provider == 'curate'):
            self.manifest_hash['provider'] = [self._rbsc_proivider()]
        elif (provider == 'hesb'):
            self.manifest_hash['provider'] = [self._hesb_proivider()]
        else:
            raise Exception("bad provider " + provider.lower())

    def _snite_proivider(self):
        return {
            "id": "https://sniteartmuseum.nd.edu/about-us/contact-us/",
            "type": "Agent",
            "label": {"en": ["Snite Museum of Art"]},
            "homepage": [
                {
                  "id": "https://sniteartmuseum.nd.edu",
                  "type": "Text",
                  "label": {"en": ["Snite Museum of Art"]},
                  "format": "text/html"
                }
            ],
            "logo": [
                {
                    "id": "https://sniteartmuseum.nd.edu/stylesheets/images/snite_logo@2x.png",
                    "type": "Image",
                    "format": "image/png",
                    "height": 100,
                    "width": 120
                }
            ]
        }

    def _rbsc_proivider(self):
        return {
            "id": "https://rarebooks.library.nd.edu/using",
            "type": "Agent",
            "label": {"en": ["Rare Books and Special Collections, Hesburgh Libraries, University of Notre Dame"]},
            "homepage": [
                {
                  "id": "https://rarebooks.library.nd.edu/",
                  "type": "Text",
                  "label": {"en": ["Rare Books and Special Collections, Hesburgh Libraries, University of Notre Dame"]},
                  "format": "text/html"
                }
            ],
            "logo": [
                {
                    "id": "https://rarebooks.library.nd.edu/images/hesburgh_mark.png",
                    "type": "Image",
                    "format": "image/png",
                    "height": 100,
                    "width": 120
                }
            ]
        }

    def _archives_proivider(self):
        return {
            "id": "http://archives.nd.edu/about/",
            "type": "Agent",
            "label": {"en": ["University of Notre Dame Archives, Hesburgh Libraries, University of Notre Dame"]},
            "homepage": [
                {
                  "id": "http://archives.nd.edu/",
                  "type": "Text",
                  "label": {"en": ["University of Notre Dame Archives"]},
                  "format": "text/html"
                }
            ],
            "logo": [
                {
                    "id": "https://rarebooks.library.nd.edu/images/hesburgh_mark.png",
                    "type": "Image",
                    "format": "image/png",
                    "height": 100,
                    "width": 120
                }
            ]
        }

    def _hesb_proivider(self):
        return {
            "id": "https://library.nd.edu",
            "type": "Agent",
            "label": {"en": ["General Collection, Hesburgh Libraries"]},
            "homepage": [
                {
                  "id": "https://library.nd.edu/",
                  "type": "Text",
                  "label": {"en": ["General Collection, Hesburgh Libraries"]},
                  "format": "text/html"
                }
            ],
            "logo": [
                {
                    "id": "https://library.nd.edu/static/media/library.logo.43a05388.png",
                    "type": "Image",
                    "format": "image/png",
                    "height": 100,
                    "width": 120
                }
            ]
        }

    def _annotation_page_id(self):
        # return self._manifest_id() + '/annotation_page/' + self.id
        return os.path.join(self.iiif_base_url, 'annotation_page', self.id)

    def _search_for_default_image(self, data):
        for file_json in data.files():
            return file_json

        # if data.type() == 'file':
        #     return data

        # for child in data.children():
        #     if child.type == 'file':
        #         return child

        #     return self._search_for_default_image(child)

        return False

    def _metadata_keys_that_have_top_level_values(self):
        return [
            'title',
            'provider',
            'creator',
            'description',
            'collectioninformation',
            'repository',
            'copyrightStatus',
            'copyrightStatement',
            'usage',
            'license',
            'thumbnail',
        ]

    def item_has_pdf(self, item_data):
        return item_data.get('mimeType') == 'application/pdf' or item_data.get('sourceFilePath', '').endswith('.pdf') or item_data.get('filePath', '').endswith('.pdf')
