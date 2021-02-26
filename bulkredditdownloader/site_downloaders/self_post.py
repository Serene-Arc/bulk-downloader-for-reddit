#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class SelfPost(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = Resource(self.post, self.post.url)
        out.content = self.export_to_string()
        return out

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
                   + self.post.author.name
                   + "](https://www.reddit.com/user/"
                   + self.post.author.name
                   + ")")
        return content
