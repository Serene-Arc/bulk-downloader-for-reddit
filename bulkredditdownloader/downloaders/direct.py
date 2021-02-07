#!/usr/bin/env python3

import pathlib

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.utils import GLOBAL


class Direct(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.download()

    def download(self):
        self.post['EXTENSION'] = self._get_extension(self.post['CONTENTURL'])
        self.directory.mkdir(exist_ok=True)

        filename = GLOBAL.config['filename'].format(**self.post) + self.post["EXTENSION"]
        self._download_resource(pathlib.Path(filename), self.directory, self.post['CONTENTURL'])
