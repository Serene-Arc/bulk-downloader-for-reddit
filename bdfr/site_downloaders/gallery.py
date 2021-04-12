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


class Gallery(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        image_urls = self._get_links(self.post.url)
        if not image_urls:
            raise SiteDownloaderError('No images found in Reddit gallery')
        return [Resource(self.post, url) for url in image_urls]

    @staticmethod
    def _get_links(url: str) -> list[str]:
        resource_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }
        page = Gallery.retrieve_url(url, headers=resource_headers)
        soup = bs4.BeautifulSoup(page.text, 'html.parser')

        links = soup.findAll('a', attrs={'target': '_blank', 'href': re.compile(r'https://preview\.redd\.it.*')})
        links = [link.get('href') for link in links]
        return links
