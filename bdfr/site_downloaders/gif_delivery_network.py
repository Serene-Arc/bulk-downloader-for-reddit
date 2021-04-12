#!/usr/bin/env python3

from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bdfr.exceptions import NotADownloadableLinkError, SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class GifDeliveryNetwork(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        media_url = self._get_link(self.post.url)
        return [Resource(self.post, media_url, '.mp4')]

    @staticmethod
    def _get_link(url: str) -> str:
        page = GifDeliveryNetwork.retrieve_url(url)

        soup = BeautifulSoup(page.text, 'html.parser')
        content = soup.find('source', attrs={'id': 'mp4Source', 'type': 'video/mp4'})

        try:
            out = content['src']
            if not out:
                raise KeyError
        except KeyError:
            raise SiteDownloaderError('Could not find source link')

        return out
