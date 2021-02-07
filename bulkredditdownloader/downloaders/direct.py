import os
import pathlib

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.utils import GLOBAL


class Direct(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        post['EXTENSION'] = self.getExtension(post['CONTENTURL'])
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post) + post["EXTENSION"]
        short_filename = post['POSTID'] + post['EXTENSION']

        self.getFile(filename, short_filename, directory, post['CONTENTURL'])
