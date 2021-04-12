#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class SelfPost(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = Resource(self.post, self.post.url, '.txt')
        out.content = self.export_to_string().encode('utf-8')
        out.create_hash()
        return [out]

    def export_to_string(self) -> str:
        """Self posts are formatted here"""
        content = ("## ["
                   + self.post.fullname
                   + "]("
                   + self.post.url
                   + ")\n"
                   + self.post.selftext
                   + "\n\n---\n\n"
                   + "submitted to [r/"
                   + self.post.subreddit.title
                   + "](https://www.reddit.com/r/"
                   + self.post.subreddit.title
                   + ") by [u/"
                   + (self.post.author.name if self.post.author else "DELETED")
                   + "](https://www.reddit.com/user/"
                   + (self.post.author.name if self.post.author else "DELETED")
                   + ")")
        return content
