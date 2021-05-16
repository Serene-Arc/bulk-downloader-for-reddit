#!/usr/bin/env python3

import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.redgifs import Redgifs


class Gfycat(Redgifs):
    def __init__(self, post: Submission):
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        return super().find_resources(authenticator)

    @staticmethod
    def _get_link(url: str) -> str:
        gfycat_id = re.match(r'.*/(.*?)/?$', url).group(1)
        url = 'https://gfycat.com/' + gfycat_id

        response = Gfycat.retrieve_url(url)
        if re.search(r'(redgifs|gifdeliverynetwork)', response.url):
            url = url.lower()  # Fixes error with old gfycat/redgifs links
            return Redgifs._get_link(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('script', attrs={'data-react-helmet': 'true', 'type': 'application/ld+json'})

        try:
            out = json.loads(content.contents[0])['video']['contentUrl']
        except (IndexError, KeyError, AttributeError) as e:
            raise SiteDownloaderError(f'Failed to download Gfycat link {url}: {e}')
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f'Did not receive valid JSON data: {e}')
        return out
