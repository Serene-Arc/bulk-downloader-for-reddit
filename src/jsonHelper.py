import json
from os import path, remove

from src.errors import InvalidJSONFile


class JsonFile:
    """ Write and read JSON files

    Use add(self,toBeAdded) to add to files

    Use delete(self,*deletedKeys) to delete keys
    """

    FILEDIR = ""

    def __init__(self, FILEDIR):
        self.FILEDIR = FILEDIR
        if not path.exists(self.FILEDIR):
            self.__writeToFile({}, create=True)

    def read(self):
        try:
            with open(self.FILEDIR, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            raise InvalidJSONFile(f"{self.FILEDIR} cannot be read")

    def add(self, toBeAdded, sub=None):
        """Takes a dictionary and merges it with json file.
        It uses new key's value if a key already exists.
        Returns the new content as a dictionary.
        """

        data = self.read()
        if sub:
            data[sub] = {**data[sub], **toBeAdded}
        else:
            data = {**data, **toBeAdded}
        self.__writeToFile(data)
        return self.read()

    def delete(self, *deleteKeys):
        """Delete given keys from JSON file.
        Returns the new content as a dictionary.
        """

        data = self.read()
        for deleteKey in deleteKeys:
            if deleteKey in data:
                del data[deleteKey]
                found = True
        if not found:
            return False
        self.__writeToFile(data)

    def __writeToFile(self, content, create=False):
        if not create:
            remove(self.FILEDIR)
        with open(self.FILEDIR, 'w') as f:
            json.dump(content, f, indent=4)
