#!/usr/bin/env python3

import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.gif_delivery_network import GifDeliveryNetwork


class Redgifs(GifDeliveryNetwork):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return super().find_resources(authenticator)

    @staticmethod
    def _get_link(url: str) -> str:
        try:
            redgif_id = re.match(r'.*/(.*?)/?$', url).group(1)
        except AttributeError:
            raise SiteDownloaderError(f'Could not extract Redgifs ID from {url}')

        url = f'https://api.redgifs.com/v1/gfycats/{redgif_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/90.0.4430.93 Safari/537.36',
        }

        content = Redgifs.retrieve_url(url, headers=headers)

        if content is None:
            raise SiteDownloaderError('Could not read the page source')

        try:
            out = content.json()["gfyItem"]["mp4Url"]
        except (IndexError, KeyError, AttributeError):
            raise SiteDownloaderError('Failed to find JSON data in page')
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f'Received data was not valid JSON: {e}')

        return out
