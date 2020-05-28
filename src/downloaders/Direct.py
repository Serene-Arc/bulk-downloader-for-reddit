import os

from src.downloaders.downloaderUtils import getFile, getExtension

from src.errors import FileNameTooLong
from src.utils import nameCorrector
from src.utils import printToFile as print

class Direct:
    def __init__(self,directory,POST):
        POST['postExt'] = getExtension(POST['postURL'])
        if not os.path.exists(directory): os.makedirs(directory)
        title = nameCorrector(POST['postTitle'])

        """Filenames are declared here"""

        print(POST["postSubmitter"]+"_"+title+"_"+POST['postId']+POST['postExt'])

        fileDir = directory / (
            POST["postSubmitter"]+"_"+title+"_"+POST['postId']+POST['postExt']
        )
        tempDir = directory / (
            POST["postSubmitter"]+"_"+title+"_"+POST['postId']+".tmp"
        )

        try:
            getFile(fileDir,tempDir,POST['postURL'])
        except FileNameTooLong:
            fileDir = directory / (POST['postId']+POST['postExt'])
            tempDir = directory / (POST['postId']+".tmp")

            getFile(fileDir,tempDir,POST['postURL'])