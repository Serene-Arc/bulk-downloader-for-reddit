#!/usr/bin/env python3

import json
import re
from typing import Optional

from cachetools import TTLCache, cached
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Redgifs(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        media_urls = self._get_link(self.post.url)
        return [Resource(self.post, m, Resource.retry_download(m), None) for m in media_urls]

    @staticmethod
    @cached(cache=TTLCache(maxsize=5, ttl=82080))
    def _get_auth_token() -> str:
        token = json.loads(Redgifs.retrieve_url("https://api.redgifs.com/v2/auth/temporary").text)["token"]
        return token

    @staticmethod
    def _get_id(url: str) -> str:
        try:
            if url.endswith("/"):
                url = url.removesuffix("/")
            redgif_id = re.match(r".*/(.*?)(?:#.*|\?.*|\..{0,})?$", url).group(1).lower()
            redgif_id = re.sub(r"(-.*)$", "", redgif_id)
        except AttributeError:
            raise SiteDownloaderError(f"Could not extract Redgifs ID from {url}")
        return redgif_id

    @staticmethod
    def _get_link(url: str) -> set[str]:
        redgif_id = Redgifs._get_id(url)

        auth_token = Redgifs._get_auth_token()
        if not auth_token:
            raise SiteDownloaderError("Unable to retrieve Redgifs API token")

        headers = {
            "referer": "https://www.redgifs.com/",
            "origin": "https://www.redgifs.com",
            "content-type": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }
        content = Redgifs.retrieve_url(f"https://api.redgifs.com/v2/gifs/{redgif_id}", headers=headers)

        if content is None:
            raise SiteDownloaderError("Could not read the page source")

        try:
            response_json = json.loads(content.text)
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f"Received data was not valid JSON: {e}")

        out = set()
        try:
            if response_json["gif"]["type"] == 1:  # type 1 is a video
                if Redgifs.head_url(response_json["gif"]["urls"]["hd"], headers=headers).status_code == 200:
                    out.add(response_json["gif"]["urls"]["hd"])
                else:
                    out.add(response_json["gif"]["urls"]["sd"])
            elif response_json["gif"]["type"] == 2:  # type 2 is an image
                if gallery := response_json["gif"]["gallery"]:
                    content = Redgifs.retrieve_url(f"https://api.redgifs.com/v2/gallery/{gallery}")
                    response_json = json.loads(content.text)
                    out = {p["urls"]["hd"] for p in response_json["gifs"]}
                else:
                    out.add(response_json["gif"]["urls"]["hd"])
            else:
                raise KeyError
        except (KeyError, AttributeError):
            raise SiteDownloaderError("Failed to find JSON data in page")

        return out
