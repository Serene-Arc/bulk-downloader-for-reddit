#!/usr/bin/env python3

import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Redgifs(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        media_url = self._get_link(self.post.url)
        return [Resource(self.post, media_url, '.mp4')]

    @staticmethod
    def _get_link(url: str) -> str:
        try:
            redgif_id = re.match(r'.*/(.*?)/?$', url).group(1)
        except AttributeError:
            raise SiteDownloaderError(f'Could not extract Redgifs ID from {url}')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.93 Safari/537.36',
        }

        content = Redgifs.retrieve_url(f'https://api.redgifs.com/v1/gfycats/{redgif_id}', headers=headers)

        if content is None:
            raise SiteDownloaderError('Could not read the page source')

        try:
            out = json.loads(content.text)['gfyItem']['mp4Url']
        except (KeyError, AttributeError):
            raise SiteDownloaderError('Failed to find JSON data in page')
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f'Received data was not valid JSON: {e}')

        return out
