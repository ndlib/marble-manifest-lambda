def load_standard_json_into_item_class(id: str, standard_json: dict):
    return Item(standard_json, standard_json)


class Item():

    def __init__(self, object, all_objects, parent=None):
        self.parent = parent
        self.object = object
        self.all_objects = all_objects

    def repository(self):
        return self.collection().get('sourceSystem', 'aleph')

    def type(self):
        if not self.get('level', False):  # Note:  files don't contain "level" in graphql
            self.object['level'] = 'file'  # Set leel to 'file'
            return('file')  # return 'file'
        return self.get('level')

    def collection(self):
        return Item(self.all_objects, self.all_objects)

    def root(self):
        return self.get("parentId", False) == "root"

    def get(self, key, default=False):
        return self.object.get(key, default)

    def children(self) -> list:
        return map(lambda item: Item(item, self.all_objects, self.object), self.object.get("children", {}).get("items", []))

    def files(self) -> list:
        return self.object.get('files', {}).get('items', [])

    def files_object(self) -> list:
        return map(lambda item: Item(item, self.all_objects, self.object), self.object.get('files', {}).get('items', []))

    def _find_row(self, id, parent):
        for this_row in parent.children():
            if this_row.get('id', False) == id:
                return Item(this_row, self.all_objects)
        return False
