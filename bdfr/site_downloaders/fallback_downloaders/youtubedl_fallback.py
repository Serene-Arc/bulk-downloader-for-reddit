#!/usr/bin/env python3
# coding=utf-8

import logging
from typing import Optional

import youtube_dl
from praw.models import Submission

from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.fallback_downloaders.fallback_downloader import BaseFallbackDownloader
from bdfr.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class YoutubeDlFallback(BaseFallbackDownloader, Youtube):
    def __init__(self, post: Submission):
        super(YoutubeDlFallback, self).__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = super()._download_video({})
        return [out]

    @staticmethod
    def can_handle_link(url: str) -> bool:
        yt_logger = logging.getLogger('youtube-dl')
        yt_logger.setLevel(logging.CRITICAL)
        with youtube_dl.YoutubeDL({
            'logger': yt_logger,
        }) as ydl:
            try:
                result = ydl.extract_info(url, download=False)
                if result:
                    return True
            except Exception as e:
                logger.exception(e)
                return False
        return False
