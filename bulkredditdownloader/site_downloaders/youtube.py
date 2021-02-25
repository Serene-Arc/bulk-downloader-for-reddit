#!/usr/bin/env python3

import logging
import tempfile
from typing import Optional

import youtube_dl
from praw.models import Submission

from bulkredditdownloader.authenticator import Authenticator
from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Youtube(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[Authenticator] = None) -> list[Resource]:
        return [self._download_video()]

    def _download_video(self) -> Resource:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "format": "best",
                "outtmpl": str(temp_dir / "test.%(ext)s"),
                "playlistend": 1,
                "nooverwrites": True,
                "quiet": True
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.post.url])

            with open(temp_dir / 'test.mp4', 'rb') as file:
                content = file.read()
        out = Resource(self.post, self.post.url)
        out.content = content
        return out
