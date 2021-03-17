#!/usr/bin/env python3

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from praw.models import Submission

from bulkredditdownloader.exceptions import NotADownloadableLinkError
from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader


class GifDeliveryNetwork(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        media_url = self._get_link(self.post.url)
        return [Resource(self.post, media_url, '.mp4')]

    @staticmethod
    def _get_link(url: str) -> str:
        if re.match(r'https://.*\.(mp4|webm|gif)(\?.*)?$', url):
            return url

        page_source = requests.get(url).text

        soup = BeautifulSoup(page_source, 'html.parser')
        content = soup.find('source', attrs={'id': 'mp4Source', 'type': 'video/mp4'})

        if content is None or content.get('src') is None:
            raise NotADownloadableLinkError('Could not read the page source')

        return content.get('src')
