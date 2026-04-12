#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.fallback_downloaders.fallback_downloader import BaseFallbackDownloader
from bdfr.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class YtdlpFallback(BaseFallbackDownloader, Youtube):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = Resource(
            self.post,
            self.post.url,
            super()._download_video({}),
            super().get_video_attributes(self.post.url)["ext"],
        )
        return [out]

    @staticmethod
    def can_handle_link(url: str) -> bool:
        try:
            attributes = YtdlpFallback.get_video_attributes(url)
        except NotADownloadableLinkError:
            return False
        if attributes:
            return True
