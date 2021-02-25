import os

from src.downloaders.downloaderUtils import getFile, getExtension
from src.utils import GLOBAL


class Direct:
    def __init__(self, directory, POST):
        POST['EXTENSION'] = getExtension(POST['CONTENTURL'])
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**POST) + POST["EXTENSION"]
        shortFilename = POST['POSTID'] + POST['EXTENSION']

        getFile(filename, shortFilename, directory, POST['CONTENTURL'])
