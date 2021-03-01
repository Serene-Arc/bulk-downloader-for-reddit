#!/usr/bin/env python3

import logging
from typing import Optional

from praw.models import Submission

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class VReddit(Youtube):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = super()._download_video({})
        return [out]
