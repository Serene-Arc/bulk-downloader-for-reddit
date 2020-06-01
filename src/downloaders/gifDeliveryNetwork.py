import json
import os
import urllib.request
from bs4 import BeautifulSoup

from src.downloaders.downloaderUtils import getFile, getExtension
from src.errors import (FileNameTooLong, AlbumNotDownloadedCompletely, 
                        NotADownloadableLinkError, FileAlreadyExistsError)
from src.utils import GLOBAL
from src.utils import printToFile as print

class GifDeliveryNetwork:
    def __init__(self,directory,POST):
        try:
            POST['MEDIAURL'] = self.getLink(POST['CONTENTURL'])
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")

        POST['EXTENSION'] = getExtension(POST['MEDIAURL'])
        
        if not os.path.exists(directory): os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**POST)+POST["EXTENSION"]
        shortFilename = POST['POSTID']+POST['EXTENSION']
        
        getFile(filename,shortFilename,directory,POST['MEDIAURL'])
    
    @staticmethod
    def getLink(url):
        """Extract direct link to the video from page's source
        and return it
        """

        if '.webm' in url.split('/')[-1] or '.mp4' in url.split('/')[-1] or '.gif' in url.split('/')[-1]:
            return url

        if url[-1:] == '/':
            url = url[:-1]

        url = "https://www.gifdeliverynetwork.com/" + url.split('/')[-1]

        pageSource = (urllib.request.urlopen(url).read().decode())

        soup = BeautifulSoup(pageSource, "html.parser")
        attributes = {"id":"mp4Source","type":"video/mp4"}
        content = soup.find("source",attrs=attributes)

        if content is None:
            
            raise NotADownloadableLinkError("Could not read the page source")

        return content["src"]