#!/usr/bin/env python3

import json
import re
from typing import Optional

from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Imgur(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)
        self.raw_data = {}

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        self.raw_data = self._get_data(self.post.url)

        out = []
        if "is_album" in self.raw_data:
            for image in self.raw_data["images"]:
                if "mp4" in image:
                    out.append(Resource(self.post, image["mp4"], Resource.retry_download(image["mp4"])))
                else:
                    out.append(Resource(self.post, image["link"], Resource.retry_download(image["link"])))
        else:
            if "mp4" in self.raw_data:
                out.append(Resource(self.post, self.raw_data["mp4"], Resource.retry_download(self.raw_data["mp4"])))
            else:
                out.append(Resource(self.post, self.raw_data["link"], Resource.retry_download(self.raw_data["link"])))
        return out

    @staticmethod
    def _get_id(link: str) -> str:
        try:
            imgur_id = re.search(r"imgur\.com/(?:a/|gallery/)?([a-zA-Z0-9]+)", link).group(1)
        except AttributeError:
            raise SiteDownloaderError(f"Could not extract Imgur ID from {link}")
        return imgur_id

    @staticmethod
    def _get_data(link: str) -> dict:
        imgur_id = Imgur._get_id(link)
        if re.search(r"/(gallery|a)/", link):
            api = f"https://api.imgur.com/3/album/{imgur_id}"
        else:
            api = f"https://api.imgur.com/3/image/{imgur_id}"

        headers = {
            "referer": "https://imgur.com/",
            "origin": "https://imgur.com",
            "content-type": "application/json",
            "Authorization": "Client-ID 546c25a59c58ad7",
        }
        res = Imgur.retrieve_url(api, headers=headers)

        try:
            image_dict = json.loads(res.text)
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f"Could not parse received response as JSON: {e}")

        return image_dict["data"]
