#!/usr/bin/env python3

import logging
import re
from typing import Optional

import bs4
import requests
from praw.models import Submission

from bulkredditdownloader.exceptions import NotADownloadableLinkError
from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Erome(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        images = self._get_links(self.post.url)
        if not images:
            raise NotADownloadableLinkError('Erome parser could not find any links')

        if len(images) == 1:
            image = images.pop()
            image = self._validate_url(image)
            return [Resource(self.post, image)]

        else:
            out = []
            for i, image in enumerate(images):
                image = self._validate_url(image)
                out.append(Resource(self.post, image))
            return out

    @staticmethod
    def _validate_url(image):
        if not re.match(r'https?://.*', image):
            image = "https://" + image
        return image

    @staticmethod
    def _get_links(url: str) -> set[str]:
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text)
        front_images = soup.find_all('img', attrs={'class': 'img-front'})
        out = [im.get('src') for im in front_images]

        videos = soup.find_all('source')
        out.extend([vid.get('src') for vid in videos])

        return set(out)
