import os

from src.downloaders.downloaderUtils import getFile, getExtension

from src.errors import FileNameTooLong
from src.utils import GLOBAL
from src.utils import printToFile as print

class Direct:
    def __init__(self,directory,POST):
        POST['EXTENSION'] = getExtension(POST['CONTENTURL'])
        if not os.path.exists(directory): os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**POST)+POST["EXTENSION"]
        shortFilename = POST['POSTID']+POST['EXTENSION']

        getFile(filename,shortFilename,directory,POST['CONTENTURL'])
        