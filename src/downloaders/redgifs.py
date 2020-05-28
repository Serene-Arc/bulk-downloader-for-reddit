import json
import os
import urllib.request
from bs4 import BeautifulSoup

from src.downloaders.downloaderUtils import getFile, getExtension
from src.errors import (FileNameTooLong, AlbumNotDownloadedCompletely, 
                        NotADownloadableLinkError, FileAlreadyExistsError)
from src.utils import nameCorrector
from src.utils import printToFile as print

class Redgifs:
    def __init__(self,directory,POST):
        try:
            POST['mediaURL'] = self.getLink(POST['postURL'])
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")

        POST['postExt'] = getExtension(POST['mediaURL'])

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
            getFile(fileDir,tempDir,POST['mediaURL'])
        except FileNameTooLong:
            fileDir = directory / (POST['postId']+POST['postExt'])
            tempDir = directory / (POST['postId']+".tmp")

            getFile(fileDir,tempDir,POST['mediaURL'])

    def getLink(self, url):
        """Extract direct link to the video from page's source
        and return it
        """

        if '.webm' in url or '.mp4' in url or '.gif' in url:
            return url

        if url[-1:] == '/':
            url = url[:-1]

        url = "https://redgifs.com/watch/" + url.split('/')[-1]

        pageSource = (urllib.request.urlopen(url).read().decode())

        soup = BeautifulSoup(pageSource, "html.parser")
        attributes = {"data-react-helmet":"true","type":"application/ld+json"}
        content = soup.find("script",attrs=attributes)

        if content is None:
            raise NotADownloadableLinkError("Could not read the page source")

        return json.loads(content.contents[0])["video"]["contentUrl"]