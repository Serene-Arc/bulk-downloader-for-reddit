#!/usr/bin/env python3

from praw.models import Submission

from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader


class Direct(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def download(self):
        return [self._download_resource(self.post.url)]
