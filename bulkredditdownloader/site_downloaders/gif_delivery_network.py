#!/usr/bin/env python3

import pathlib
import urllib.request

from bs4 import BeautifulSoup

from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.errors import NotADownloadableLinkError
from bulkredditdownloader.utils import GLOBAL


class GifDeliveryNetwork(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.download()

    def download(self):
        try:
            self.post['MEDIAURL'] = self._get_link(self.post['CONTENTURL'])
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")

        self.post['EXTENSION'] = self._get_extension(self.post['MEDIAURL'])
        self.directory.mkdir(exist_ok=True)

        filename = GLOBAL.config['filename'].format(**self.post) + self.post["EXTENSION"]

        self._download_resource(filename, self.directory, self.post['MEDIAURL'])

    @staticmethod
    def _get_link(url: str) -> str:
        """Extract direct link to the video from page's source
        and return it
        """
        if '.webm' in url.split('/')[-1] or '.mp4' in url.split('/')[-1] or '.gif' in url.split('/')[-1]:
            return url

        if url[-1:] == '/':
            url = url[:-1]

        url = "https://www.gifdeliverynetwork.com/" + url.split('/')[-1]
        page_source = (urllib.request.urlopen(url).read().decode())

        soup = BeautifulSoup(page_source, "html.parser")
        attributes = {"id": "mp4Source", "type": "video/mp4"}
        content = soup.find("source", attrs=attributes)

        if content is None:
            raise NotADownloadableLinkError("Could not read the page source")

        return content["src"]
