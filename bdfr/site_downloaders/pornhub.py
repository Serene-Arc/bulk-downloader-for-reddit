#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class PornHub(Youtube):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        ytdl_options = {
            "format": "best",
            "nooverwrites": True,
        }
        if video_attributes := super().get_video_attributes(self.post.url):
            extension = video_attributes["ext"]
        else:
            raise SiteDownloaderError()

        out = Resource(
            self.post,
            self.post.url,
            super()._download_video(ytdl_options),
            extension,
        )
        return [out]
