#!/usr/bin/env python3

import logging
import re
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Erome(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self._get_links(self.post.url)

        if not links:
            raise SiteDownloaderError('Erome parser could not find any links')

        out = []
        for link in links:
            if not re.match(r'https?://.*', link):
                link = 'https://' + link
            out.append(Resource(self.post, link))
        return out

    @staticmethod
    def _get_links(url: str) -> set[str]:
        page = Erome.retrieve_url(url)
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        front_images = soup.find_all('img', attrs={'class': 'lasyload'})
        out = [im.get('data-src') for im in front_images]

        videos = soup.find_all('source')
        out.extend([vid.get('src') for vid in videos])

        return set(out)
