#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class VReddit(Youtube):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        ytdl_options = {
            "playlistend": 1,
            "nooverwrites": True,
        }
        download_function = self._download_video(ytdl_options)
        extension = self.get_video_attributes(self.post.url)["ext"]
        res = Resource(self.post, self.post.url, download_function, extension)
        return [res]

    @staticmethod
    def get_video_attributes(url: str) -> dict:
        result = VReddit.get_video_data(url)
        if "ext" in result:
            return result
        else:
            try:
                result = result["entries"][0]
                return result
            except Exception as e:
                logger.exception(e)
                raise NotADownloadableLinkError(f"Video info extraction failed for {url}")
