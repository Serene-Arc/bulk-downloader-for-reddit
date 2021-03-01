#!/usr/bin/env python3

import logging
import tempfile
from pathlib import Path
from typing import Optional

import youtube_dl
from praw.models import Submission

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Youtube(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        ytdl_options = {
            "format": "best",
            "playlistend": 1,
            "nooverwrites": True,
        }
        out = self._download_video(ytdl_options)
        return [out]

    def _download_video(self, ytdl_options: dict) -> Resource:
        ytdl_options['quiet'] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            download_path = Path(temp_dir).resolve()
            ytdl_options['outtmpl'] = str(download_path) + '/' + 'test.%(ext)s'
            with youtube_dl.YoutubeDL(ytdl_options) as ydl:
                ydl.download([self.post.url])

            downloaded_file = list(download_path.iterdir())[0]
            extension = downloaded_file.suffix
            with open(downloaded_file, 'rb') as file:
                content = file.read()
        out = Resource(self.post, self.post.url, extension)
        out.content = content
        out.create_hash()
        return out
