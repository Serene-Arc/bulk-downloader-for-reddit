import os
import pathlib

from bulkredditdownloader.downloaders.downloader_utils import getExtension, getFile
from bulkredditdownloader.utils import GLOBAL


class Direct:
    def __init__(self, directory: pathlib.Path, post: dict):
        post['EXTENSION'] = getExtension(post['CONTENTURL'])
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post) + post["EXTENSION"]
        short_filename = post['POSTID'] + post['EXTENSION']

        getFile(filename, short_filename, directory, post['CONTENTURL'])
