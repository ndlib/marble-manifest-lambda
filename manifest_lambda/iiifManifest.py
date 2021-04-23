import os
import re
from iiifImage import iiifImage


class iiifManifest():
    def __init__(self, iiif_base_url: str, standard_json: dict, mapping_template: dict):
        self.iiif_base_url = iiif_base_url
        self.mapping_template = mapping_template
        self.standard_json = standard_json
        self.lang = 'en'
        self.type = self._schema_to_manifest_type()
        self.manifest_hash = {}
        self._build_mainfest()

    def manifest(self):
        return self.manifest_hash

    def key_exists(self, key):
        return key in self.standard_json and self.standard_json.get(key)

    def metadata_array(self):
        keys_in_other_parts_of_manifest = _metadata_keys_that_have_top_level_values()
        ret = []
        for key in self.mapping_template.keys():
            if key.lower() != 'n/a':
                if key in ('creators', 'contributors', 'publishers', 'languages', 'subjects', 'collections'):
                    value = self.standard_json.get(key)
                    if value:
                        value = list(map(lambda row: row.get('display', ''), value))
                else:
                    value = self.standard_json.get(key, False)

                label = self.mapping_template.get(key, {}).get('marble_title', False)
                # print("key = ", key, "label =", label)
                if label and value and key not in keys_in_other_parts_of_manifest and label.lower() != 'n/a':
                    ret.append(_convert_label_value(self.lang, label, value))

        return ret

    def thumbnail(self):
        if self.standard_json.get('defaultFile', False):
            return [iiifImage(self.standard_json.get('defaultFile'), self.iiif_base_url).thumbnail()]
        if self.type == 'Canvas':
            return [iiifImage(self.standard_json, self.iiif_base_url).thumbnail()]
        file_json = _search_for_default_image(self.standard_json)
        if file_json:
            return [iiifImage(file_json, self.iiif_base_url).thumbnail()]

        return []

    def _build_mainfest(self):
        label_contents = self.standard_json.get('title')
        if not label_contents:  # file records do not have a title field
            label_contents = self.standard_json.get('id')
        self.manifest_hash = {
            'type': self.type,
            'id': self._manifest_id(self.standard_json.get('id')),
            'label': _lang_wrapper(self.lang, label_contents),
            'thumbnail': self.thumbnail(),
            'items': self._items(),
            'viewingDirection': 'left-to-right'
        }
        part_of = _return_part_of(self.type, self.standard_json.get('parentId'), self.standard_json.get('parent', {}).get('level'), self.iiif_base_url)
        if part_of:
            self.manifest_hash["partOf"] = part_of
        self.add_context()
        provider = _return_provider(self.standard_json.get('repository'), self.standard_json.get('level', 'file'))
        if provider:
            self.manifest_hash['provider'] = [provider]
        required_statement = _return_required_statement(self.lang, self.standard_json.get('copyrightStatus'))
        if required_statement:
            self.manifest_hash['requiredStatement'] = required_statement
        rights = _return_rights(self.standard_json.get('copyrightStatement'))
        if rights:
            self.manifest_hash['rights'] = rights
        summary = _return_summary(self.lang, self.standard_json.get('description'))
        if summary:
            self.manifest_hash['summary'] = summary
        if self.type == 'Canvas':  # Unconditionally add height and width to Canvas for Mirador to work (we don't have height or width in standard json yet)
            self.manifest_hash['height'] = self.standard_json.get('height', 2000)
            self.manifest_hash['width'] = self.standard_json.get('width', 2000)

        self.add_pdf()

        metadata = self.metadata_array()
        if len(metadata) > 0:
            self.manifest_hash['metadata'] = metadata

    def _items(self):
        ret = []
        if self.type == 'Canvas':
            image = iiifImage(self.standard_json, self.iiif_base_url)
            ret.append({
                'id': _annotation_page_id(self.iiif_base_url, self.standard_json.get('id')),
                'type': 'AnnotationPage',
                'items': [
                    image.annotation(self._manifest_id(self.standard_json.get('id')))
                ]
            })
        else:
            for item_data in self.standard_json.get("children", {}).get("items", []):
                if not _item_has_pdf(item_data):
                    ret.append(iiifManifest(self.iiif_base_url, item_data, self.mapping_template).manifest())
            for file_data in self.standard_json.get("files", {}).get("items", []):
                if not _item_has_pdf(file_data):
                    ret.append(iiifManifest(self.iiif_base_url, file_data, self.mapping_template).manifest())

        return ret

    def _schema_to_manifest_type(self):
        if not self.standard_json.get('level', False):  # Note:  files don't contain "level" in graphql
            self.standard_json['level'] = 'file'  # Set leel to 'file'
        level = self.standard_json.get('level', '').lower()

        if level == 'manifest':
            return 'Manifest'
        elif level == 'collection':
            return 'Collection'
        elif level == 'file':
            return 'Canvas'
        elif level:  # Note: graphql File doesn't contain a "level"
            return 'Canvas'
        raise Exception("invalid schema processor type: " + level)

    def _manifest_id(self, item_id: str):
        manifest_type_dict = {'Collection': 'manifest', 'Manifest': 'manifest', 'Canvas': 'canvas'}
        type_of_manifest_piece = manifest_type_dict.get(self.type)
        return os.path.join(self.iiif_base_url, type_of_manifest_piece, item_id.replace("/", "%2F"))

    def add_context(self):
        if self.standard_json.get("parentId", False) == "root":
            self.manifest_hash["@context"] = [
                "http://www.w3.org/ns/anno.jsonld",
                "https://presentation-iiif.library.nd.edu/extensions/partiallyDigitized",
                "http://iiif.io/api/presentation/3/context.json"
            ]

    def add_pdf(self):
        # if we are a manifest and we have a child that is a pdf add them to a render section.
        if self.type == 'Manifest':
            pdfs = []
            for item_data in self.standard_json.get("children", {}).get("items", []):
                if _item_has_pdf(item_data):
                    fileUrl = re.sub(r"^(s3:\/\/[a-zA-z_-]*?\/)", "https://rbsc.library.nd.edu/", item_data.get("filePath"))
                    pdfs.append({
                        "id": fileUrl,
                        "type": "Text",
                        "label": {"en": ["PDF Rendering"]},
                        "format": "application/pdf"
                    })

            if len(pdfs) > 0:
                self.manifest_hash['rendering'] = pdfs


def _return_summary(lang: str, description: str) -> dict:
    results = {}
    if description:
        results = _lang_wrapper(lang, description)
    return results


def _return_rights(copyright_statement: str) -> str:
    rights = ''
    if copyright_statement:
        rights = copyright_statement
    return rights


def _return_required_statement(lang: str, copyright_status: str) -> dict:
    results = {}
    if copyright_status:
        results = _convert_label_value(lang, 'Copyright', copyright_status)
    return results


def _return_part_of(manifest_type: str, parent_id: str, parent_level: str, iiif_base_url: str) -> dict:
    part_of = {}
    if manifest_type == 'Manifest':
        if parent_id != 'root' and parent_level:
            type_of_manifest_piece = 'Manifest'
            if parent_level == 'collection':
                type_of_manifest_piece = 'Collection'
            part_of = {
                "id": os.path.join(iiif_base_url, 'manifest', parent_id),
                "type": type_of_manifest_piece
            }
    return part_of


def _return_provider(repository: str, level: str) -> dict:
    if not repository or not level or level == 'file':
        return
    repository = repository.lower()
    if (repository == 'museum'):
        return _snite_proivider()
    elif (repository == 'unda'):
        return _archives_proivider()
    elif (repository == 'rare' or repository == 'curate'):
        return _rbsc_proivider()
    elif (repository == 'hesb'):
        return _hesb_proivider()
    else:
        raise Exception("bad provider " + repository.lower())
        return


def _convert_label_value(lang: str, label: str, value) -> dict:
    if (label and value):
        return {
            'label': _lang_wrapper(lang, label),
            'value': _lang_wrapper(lang, value)
        }
    return None


def _lang_wrapper(lang: str, line) -> dict:
    if type(line) != list:
        line = [line]

    line = list(map(lambda x: str(x), iter(line)))
    return {lang: line}


def _snite_proivider() -> dict:
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


def _rbsc_proivider() -> dict:
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


def _archives_proivider() -> dict:
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


def _hesb_proivider() -> dict:
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


def _annotation_page_id(iiif_base_url: str, item_id: str) -> str:
    return os.path.join(iiif_base_url, 'annotation_page', item_id.replace("/", "%2F"))


def _search_for_default_image(standard_json) -> dict:
    for file_json in standard_json.get('files', {}).get('items', []):
        return file_json


def _metadata_keys_that_have_top_level_values() -> list:
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


def _item_has_pdf(item_data):
    return item_data.get('mimeType') == 'application/pdf' or item_data.get('sourceFilePath', '').endswith('.pdf') or item_data.get('filePath', '').endswith('.pdf')
