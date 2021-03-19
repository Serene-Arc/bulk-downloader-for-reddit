#!/usr/bin/env python3

import json
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from praw.models import Submission

from bulkredditdownloader.exceptions import NotADownloadableLinkError
from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_authenticator import SiteAuthenticator
from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork


class Redgifs(GifDeliveryNetwork):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return super().find_resources(authenticator)

    @staticmethod
    def _get_link(url: str) -> str:
        if re.match(r'https://.*\.(mp4|webm|gif)(\?.*)?$', url):
            return url

        redgif_id = re.match(r'.*/(.*?)/?$', url).group(1)
        url = 'https://redgifs.com/watch/' + redgif_id

        headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                   ' Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64'
                   }

        page_source = requests.get(url, headers=headers).text

        soup = BeautifulSoup(page_source, 'html.parser')
        content = soup.find('script', attrs={'data-react-helmet': 'true', 'type': 'application/ld+json'})

        if content is None:
            raise NotADownloadableLinkError('Could not read the page source')

        out = json.loads(content.contents[0])['video']['contentUrl']
        return out
