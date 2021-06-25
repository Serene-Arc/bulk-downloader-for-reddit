#!/usr/bin/env python3

import logging
import re
from typing import Optional

import bs4
import requests
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
        image_urls = self._get_links(self.post.gallery_data['items'])
        if not image_urls:
            raise SiteDownloaderError('No images found in Reddit gallery')
        return [Resource(self.post, url) for url in image_urls]

    @ staticmethod
    def _get_links(id_dict: list[dict]) -> list[str]:
        out = []
        for item in id_dict:
            image_id = item['media_id']
            possible_extensions = ('.jpg', '.png', '.gif', '.gifv', '.jpeg')
            for extension in possible_extensions:
                test_url = f'https://i.redd.it/{image_id}{extension}'
                response = requests.head(test_url)
                if response.status_code == 200:
                    out.append(test_url)
                    break
        return out
