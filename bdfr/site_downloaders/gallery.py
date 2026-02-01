#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Gallery(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        try:
            image_urls = self._get_links(self.post.gallery_data["items"])
        except (AttributeError, TypeError):
            try:
                image_urls = self._get_links(self.post.crosspost_parent_list[0]["gallery_data"]["items"])
            except (AttributeError, IndexError, TypeError, KeyError):
                logger.error(f"Could not find gallery data in submission {self.post.id}")
                logger.exception("Gallery image find failure")
                raise SiteDownloaderError("No images found in Reddit gallery")

        if not image_urls:
            raise SiteDownloaderError("No images found in Reddit gallery")
        return [Resource(self.post, url, Resource.retry_download(url)) for url in image_urls]

    @staticmethod
    def _get_links(id_dict: list[dict]) -> list[str]:
        out = []
        for item in id_dict:
            image_id = item["media_id"]
            possible_extensions = (".jpg", ".png", ".gif", ".gifv", ".jpeg")
            for extension in possible_extensions:
                test_url = f"https://i.redd.it/{image_id}{extension}"
                if Gallery.head_url(test_url).status_code == 200:
                    out.append(test_url)
                    break
        return out
