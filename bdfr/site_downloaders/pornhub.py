#!/usr/bin/env python3
# coding=utf-8

import logging
from typing import Optional

from praw.models import Submission

from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class PornHub(Youtube):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        ytdl_options = {
            'format': 'best',
            'nooverwrites': True,
        }
        out = self._download_video(ytdl_options)
        return [out]
