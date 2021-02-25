import json
import os
import urllib.request
from bs4 import BeautifulSoup

from src.downloaders.downloaderUtils import getFile, getExtension
from src.errors import (NotADownloadableLinkError)
from src.utils import GLOBAL


class Redgifs:
    def __init__(self, directory, POST):
        try:
            POST['MEDIAURL'] = self.getLink(POST['CONTENTURL'])
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")

        POST['EXTENSION'] = getExtension(POST['MEDIAURL'])

        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**POST) + POST["EXTENSION"]
        shortFilename = POST['POSTID'] + POST['EXTENSION']

        getFile(filename, shortFilename, directory, POST['MEDIAURL'])

    @staticmethod
    def getLink(url):
        """Extract direct link to the video from page's source
        and return it
        """

        if '.webm' in url or '.mp4' in url or '.gif' in url:
            return url

        if url[-1:] == '/':
            url = url[:-1]

        url = urllib.request.Request(
            "https://redgifs.com/watch/" + url.split('/')[-1])

        url.add_header(
            'User-Agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64')

        pageSource = (urllib.request.urlopen(url).read().decode())

        soup = BeautifulSoup(pageSource, "html.parser")
        attributes = {"data-react-helmet": "true",
                      "type": "application/ld+json"}
        content = soup.find("script", attrs=attributes)

        if content is None:
            raise NotADownloadableLinkError("Could not read the page source")

        return json.loads(content.contents[0])["video"]["contentUrl"]
