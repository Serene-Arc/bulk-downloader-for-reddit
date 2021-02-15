#!/usr/bin/env python3

import urllib.request

from bs4 import BeautifulSoup
from praw.models import Submission

from bulkredditdownloader.errors import NotADownloadableLinkError
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader


class GifDeliveryNetwork(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def download(self):
        try:
            media_url = self._get_link(self.post.url)
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")

        return [self._download_resource(media_url)]

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
