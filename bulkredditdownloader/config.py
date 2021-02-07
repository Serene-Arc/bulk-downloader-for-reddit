from bulkredditdownloader.reddit import Reddit
from bulkredditdownloader.jsonHelper import JsonFile
from bulkredditdownloader.utils import nameCorrector


class Config:

    def __init__(self, filename: str):
        self.filename = filename
        self.file = JsonFile(self.filename)

    def generate(self) -> dict:
        self._validateCredentials()
        self._readCustomFileName()
        self._readCustomFolderPath()
        self._readDefaultOptions()
        return self.file.read()

    def setCustomFileName(self):
        print("""
IMPORTANT: Do not change the filename structure frequently.
           If you did, the program could not find duplicates and
           would download the already downloaded files again.
           This would not create any duplicates in the directory but
           the program would not be as snappy as it should be.

Type a template file name for each post.

You can use SUBREDDIT, REDDITOR, POSTID, TITLE, UPVOTES, FLAIR, DATE in curly braces
The text in curly braces will be replaced with the corresponding property of an each post

For example: {FLAIR}_{SUBREDDIT}_{REDDITOR}

Existing filename template:""", None if "filename" not in self.file.read() else self.file.read()["filename"])

        filename = nameCorrector(input(">> ").upper())
        self.file.add({"filename": filename})

    def _readCustomFileName(self):
        content = self.file.read()

        if "filename" not in content:
            self.file.add({"filename": "{REDDITOR}_{TITLE}_{POSTID}"})
        content = self.file.read()

        if "{POSTID}" not in content["filename"]:
            self.file.add({"filename": content["filename"] + "_{POSTID}"})

    def setCustomFolderPath(self):
        print("""
Type a folder structure (generic folder path)

Use slash or DOUBLE backslash to separate folders

You can use SUBREDDIT, REDDITOR, POSTID, TITLE, UPVOTES, FLAIR, DATE in curly braces
The text in curly braces will be replaced with the corresponding property of an each post

For example: {REDDITOR}/{SUBREDDIT}/{FLAIR}

Existing folder structure""", None if "folderpath" not in self.file.read() else self.file.read()["folderpath"])

        folderpath = nameCorrector(input(">> ").strip("\\").strip("/").upper())

        self.file.add({"folderpath": folderpath})

    def _readCustomFolderPath(self, path=None):
        content = self.file.read()
        if "folderpath" not in content:
            self.file.add({"folderpath": "{SUBREDDIT}"})

    def setDefaultOptions(self):
        print("""
Type options to be used everytime script runs

For example: --no-dupes --quit --limit 100 --skip youtube.com

Existing default options:""", None if "options" not in self.file.read() else self.file.read()["options"])

        options = input(">> ").strip("")

        self.file.add({"options": options})

    def _readDefaultOptions(self):
        content = self.file.read()
        if "options" not in content:
            self.file.add({"options": ""})

    def _validateCredentials(self):
        """Read credentials from config.json file"""
        try:
            content = self.file.read()["credentials"]
        except BaseException:
            self.file.add({"credentials": {}})
            content = self.file.read()["credentials"]

        if "reddit" in content and len(content["reddit"]) != 0:
            pass
        else:
            Reddit().begin()
        print()

    def setDefaultDirectory(self):
        print("""Set a default directory to use in case no directory is given
Leave blank to reset it. You can use {time} in foler names to use to timestamp it
For example: D:/archive/BDFR_{time}
""")
        print("Current default directory:", self.file.read()[
              "default_directory"] if "default_directory" in self.file.read() else "")
        self.file.add({"default_directory": input(">> ")})
