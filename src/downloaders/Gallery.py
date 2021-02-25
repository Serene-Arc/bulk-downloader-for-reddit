import os

from src.downloaders.downloaderUtils import getFile, getExtension

from src.errors import FileNameTooLong
from src.utils import GLOBAL
from src.utils import printToFile as print

class Gallery:
    def __init__(self,directory,POST):
        i=0
        for key in POST['CONTENTURL']:
            i=i+1
            extension = getExtension(key)
            if not os.path.exists(directory): os.makedirs(directory)

            filename = GLOBAL.config['filename'].format(**POST)+' - '+str(i)+extension
            print(filename)
            shortFilename = POST['POSTID']+' - '+str(i)+extension

            getFile(filename,shortFilename,directory,key)