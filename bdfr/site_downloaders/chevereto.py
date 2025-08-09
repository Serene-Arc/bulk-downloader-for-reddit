import logging
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Chevereto(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self._get_links(self.post.url)
        if not links:
            raise SiteDownloaderError("Chevereto parser could not find any links")
        return [Resource(self.post, link, Resource.retry_download(link)) for link in links]

    @staticmethod
    def _get_album_links(url: str) -> list:
        image_pages = []
        album = Chevereto.retrieve_url(f"{url}")
        soup = bs4.BeautifulSoup(album.text, "html.parser")
        album_divs = soup.find("div", attrs={"class": "pad-content-listing"})
        links = album_divs.find_all("div", {"data-type": "image"})
        for link in links:
            image_pages.append(link.get("data-url-short"))
        return image_pages

    @staticmethod
    def _get_links(url: str) -> set[str]:
        resources = []
        urls = Chevereto._get_album_links(url) if "/album/" in url or "/a/" in url else [url]
        for url in urls:
            page = Chevereto.retrieve_url(url)
            soup = bs4.BeautifulSoup(page.text, "html.parser")
            image_link = soup.find("a", attrs={"data-action": lambda x: x and x.lower() == "download"}).get("href")
            resources.append(image_link)
        return set(resources)
