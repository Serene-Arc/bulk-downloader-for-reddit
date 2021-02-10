#!/usr/bin/env python3

import logging
import pathlib
import tempfile

import youtube_dl
from praw.models import Submission

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Youtube(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: Submission):
        super().__init__(directory, post)

    def download(self):
        return self._download_video()

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
        return Resource(self.post, self.post.url, content)
