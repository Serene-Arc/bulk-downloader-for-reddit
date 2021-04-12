#!/usr/bin/env python3

from typing import Optional

from praw.models import Submission

from bdfr.site_authenticator import SiteAuthenticator
from bdfr.resource import Resource
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Direct(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return [Resource(self.post, self.post.url)]
