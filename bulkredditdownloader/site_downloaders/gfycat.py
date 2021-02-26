#!/usr/bin/env python3

import json
import re
from typing import Optional

import requests
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
        """Extract direct link to the video from page's source and return it """
        if re.match(r'\.(webm|mp4|gif)$', url):
            return url

        if url.endswith('/'):
            url = url[:-1]

        url = "https://gfycat.com/" + url.split('/')[-1]

        page_source = requests.get(url).text

        soup = BeautifulSoup(page_source, "html.parser")
        attributes = {"data-react-helmet": "true", "type": "application/ld+json"}
        content = soup.find("script", attrs=attributes)

        if content is None:
            return super()._get_link(url)

        return json.loads(content.contents[0])["video"]["contentUrl"]
