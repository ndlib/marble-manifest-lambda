import json
from pathlib import Path


class MetadataMappings():

    def __init__(self, source_system: str):
        # self.data = data
        # self.provider = data.repository()
        self.source_system = source_system
        if not self.source_system:
            source_system = 'aleph'
        self.lookup = self.loadMetadataRules()
        self.standard_json_mapping = self.standard_json

    def loadMetadataRules(self):
        self.standard_json = {}
        field_definitions_json = self.load_json_file("marble", self.source_system.lower())
        for key, value in field_definitions_json.items():
            line = {
                "preferred_name": value['preferred name'],
                "schema.org": value['schema.org mapping'],
                "element": value['element'],
                "marble_title": value['marble display name'],
                "required": value['required']
            }
            self.standard_json[key] = line

    def get_by_standard_json(self, name, field):
        return self.standard_json.get(name).get(field, False)

    def get_standard_json_keys(self):
        return self.standard_json.keys()

    def load_json_file(self, site_name: str, source_name: str) -> dict:
        current_path = str(Path(__file__).parent.absolute())
        with open(current_path + "/sites/" + site_name + "/" + source_name.lower() + ".json", 'r') as input_source:
            source = json.load(input_source)
        return source
