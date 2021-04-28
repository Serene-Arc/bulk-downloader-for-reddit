#!/usr/bin/env python3

from typing import Optional

from praw.models import Submission

from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.redgifs import Redgifs


class GifDeliveryNetwork(Redgifs):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return super(GifDeliveryNetwork, self).find_resources(authenticator)

    @staticmethod
    def _get_link(url: str) -> str:
        return super(GifDeliveryNetwork, GifDeliveryNetwork)._get_link(url)
