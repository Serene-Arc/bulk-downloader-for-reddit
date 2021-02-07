import json
import os

from bulkredditdownloader.errors import InvalidJSONFile


class JsonFile:
    """ Write and read JSON files
    Use add(self,toBeAdded) to add to files
    Use delete(self,*deletedKeys) to delete keys
    """

    file_dir = ""

    def __init__(self, file_dir: str):
        self.file_dir = file_dir
        if not os.path.exists(self.file_dir):
            self.__writeToFile({}, create=True)

    def read(self) -> dict:
        try:
            with open(self.file_dir, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            raise InvalidJSONFile(f"{self.file_dir} cannot be read")

    def add(self, to_be_added: dict, sub=None) -> dict:
        """Takes a dictionary and merges it with json file.
        It uses new key's value if a key already exists.
        Returns the new content as a dictionary.
        """
        data = self.read()
        if sub:
            data[sub] = {**data[sub], **to_be_added}
        else:
            data = {**data, **to_be_added}
        self.__writeToFile(data)
        return self.read()

    def delete(self, *delete_keys: str):
        """Delete given keys from JSON file.
        Returns the new content as a dictionary.
        """
        data = self.read()
        for deleteKey in delete_keys:
            if deleteKey in data:
                del data[deleteKey]
                found = True
        if not found:
            return False
        self.__writeToFile(data)

    def __writeToFile(self, content: (dict, list, tuple), create: bool = False):
        if not create:
            os.remove(self.file_dir)
        with open(self.file_dir, 'w') as f:
            json.dump(content, f, indent=4)
