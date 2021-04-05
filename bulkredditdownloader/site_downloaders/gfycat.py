#!/usr/bin/env python3

import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork


class Gfycat(GifDeliveryNetwork):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return super().find_resources(authenticator)

    @staticmethod
    def _get_link(url: str) -> str:
        gfycat_id = re.match(r'.*/(.*?)/?$', url).group(1)
        url = 'https://gfycat.com/' + gfycat_id

        response = Gfycat.get_link(url)
        if 'gifdeliverynetwork' in response.url:
            return GifDeliveryNetwork._get_link(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('script', attrs={'data-react-helmet': 'true', 'type': 'application/ld+json'})

        out = json.loads(content.contents[0]).get('video').get('contentUrl')
        return out
