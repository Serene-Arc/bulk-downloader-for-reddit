#!/usr/bin/env python3

import json
import re
import urllib.request

from bs4 import BeautifulSoup
from praw.models import Submission

from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork


class Gfycat(GifDeliveryNetwork):
    def __init__(self, post: Submission):
        super().__init__(post)

    def download(self):
        super().download()

    @staticmethod
    def _get_link(url: str) -> str:
        """Extract direct link to the video from page's source
        and return it
        """
        if re.match(r'\.(webm|mp4|gif)$', url):
            return url

        if url.endswith('/'):
            url = url[:-1]

        url = "https://gfycat.com/" + url.split('/')[-1]

        page_source = (urllib.request.urlopen(url).read().decode())

        soup = BeautifulSoup(page_source, "html.parser")
        attributes = {"data-react-helmet": "true", "type": "application/ld+json"}
        content = soup.find("script", attrs=attributes)

        if content is None:
            return super()._get_link(url)

        return json.loads(content.contents[0])["video"]["contentUrl"]
