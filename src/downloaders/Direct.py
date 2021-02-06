import os
import pathlib

from src.downloaders.downloaderUtils import getExtension, getFile
from src.utils import GLOBAL


class Direct:
    def __init__(self, directory: pathlib.Path, post: dict):
        post['EXTENSION'] = getExtension(post['CONTENTURL'])
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post) + post["EXTENSION"]
        short_filename = post['POSTID'] + post['EXTENSION']

        getFile(filename, short_filename, directory, post['CONTENTURL'])
