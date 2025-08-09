import logging
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Imgchest(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self._get_links(self.post.url)
        if not links:
            raise SiteDownloaderError("Imgchest parser could not find any links")
        links = [Resource(self.post, link, Resource.retry_download(link)) for link in links]
        return links

    @staticmethod
    def _get_links(url: str) -> set[str]:
        page = Imgchest.retrieve_url(url)
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        album_div = soup.find("div", attrs={"id": "post-images"})
        images = album_div.find_all("img")
        out = [im.get("src") for im in images]
        videos = album_div.find_all("source")
        out.extend([vid.get("src") for vid in videos])
        return set(out)
