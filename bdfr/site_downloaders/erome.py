#!/usr/bin/env python3

import logging
import re
from collections.abc import Callable
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Erome(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self._get_links(self.post.url)

        if not links:
            raise SiteDownloaderError("Erome parser could not find any links")

        out = []
        for link in links:
            if not re.match(r"https?://.*", link):
                link = "https://" + link
            out.append(Resource(self.post, link, self.erome_download(link)))
        return out

    @staticmethod
    def _get_links(url: str) -> set[str]:
        page = Erome.retrieve_url(url)
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        front_images = soup.find_all("img", attrs={"class": "img-front"})
        out = [im.get("data-src") for im in front_images]

        videos = soup.find_all("source")
        out.extend([vid.get("src") for vid in videos])

        return set(out)

    @staticmethod
    def erome_download(url: str) -> Callable:
        download_parameters = {
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/88.0.4324.104 Safari/537.36",
                "Referer": "https://www.erome.com/",
            },
        }
        return lambda global_params: Resource.http_download(url, global_params | download_parameters)
