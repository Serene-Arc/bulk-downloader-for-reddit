#!/usr/bin/env python3

import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bdfr.exceptions import NotADownloadableLinkError, SiteDownloaderError
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

        url = 'https://redgifs.com/watch/' + redgif_id

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64',
        }

        page = Redgifs.retrieve_url(url, headers=headers)

        soup = BeautifulSoup(page.text, 'html.parser')
        content = soup.find('script', attrs={'data-react-helmet': 'true', 'type': 'application/ld+json'})

        if content is None:
            raise SiteDownloaderError('Could not read the page source')

        try:
            out = json.loads(content.contents[0])['video']['contentUrl']
        except (IndexError, KeyError):
            raise SiteDownloaderError('Failed to find JSON data in page')
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f'Received data was not valid JSON: {e}')

        return out
