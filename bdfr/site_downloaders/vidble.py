#!/usr/bin/env python3

import itertools
import logging
import re
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Vidble(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        try:
            res = self.get_links(self.post.url)
        except AttributeError:
            raise SiteDownloaderError(f"Could not read page at {self.post.url}")
        if not res:
            raise SiteDownloaderError(rf"No resources found at {self.post.url}")
        res = [Resource(self.post, r, Resource.retry_download(r)) for r in res]
        return res

    @staticmethod
    def get_links(url: str) -> set[str]:
        if not re.search(r"vidble.com/(show/|album/|watch\?v)", url):
            url = re.sub(r"/(\w*?)$", r"/show/\1", url)

        page = Vidble.retrieve_url(url)
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        content_div = soup.find("div", attrs={"id": "ContentPlaceHolder1_divContent"})
        images = content_div.find_all("img")
        images = [i.get("src") for i in images]
        videos = content_div.find_all("source", attrs={"type": "video/mp4"})
        videos = [v.get("src") for v in videos]
        resources = filter(None, itertools.chain(images, videos))
        resources = ["https://www.vidble.com" + r for r in resources]
        resources = [Vidble.change_med_url(r) for r in resources]
        return set(resources)

    @staticmethod
    def change_med_url(url: str) -> str:
        out = re.sub(r"_med(\..{3,4})$", r"\1", url)
        return out
