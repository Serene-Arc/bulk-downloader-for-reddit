import logging
from itertools import chain
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Catbox(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self.get_links(self.post.url)
        if not links:
            raise SiteDownloaderError("Catbox parser could not find any links")
        links = [Resource(self.post, link, Resource.retry_download(link)) for link in links]
        return links

    @staticmethod
    def get_links(url: str) -> set[str]:
        content = Catbox.retrieve_url(url)
        soup = bs4.BeautifulSoup(content.text, "html.parser")
        collection_div = soup.find("div", attrs={"class": "imagecontainer"})
        images = collection_div.find_all("a")
        images = [link.get("href") for link in images]
        videos = collection_div.find_all("video")
        videos = [link.get("src") for link in videos]
        audios = collection_div.find_all("audio")
        audios = [link.get("src") for link in audios]
        resources = chain(images, videos, audios)
        return set(resources)
