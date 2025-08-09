#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class DelayForReddit(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        media = DelayForReddit.retrieve_url(self.post.url)
        return [Resource(self.post, media.url, Resource.retry_download(media.url))]
