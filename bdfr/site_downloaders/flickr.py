import json
import re
from typing import Optional

from bs4 import BeautifulSoup
from cachetools import TTLCache, cached
from praw.models import Submission

from bdfr.exceptions import ResourceNotFound, SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Flickr(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)
        self.raw_data = {}

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        links = self._get_data(self.post.url)
        if not links:
            raise SiteDownloaderError("Flickr could not find any images to download")
        return [Resource(self.post, link, Resource.retry_download(link)) for link in links]

    @staticmethod
    @cached(cache=TTLCache(maxsize=5, ttl=10260))
    def _get_api_key() -> str:
        key_regex = re.compile(r".*api_key=(\w*)(&.*)?")
        res = Flickr.retrieve_url("https://www.flickr.com/services/api/response.json.html").text
        elements = BeautifulSoup(res, "html.parser")
        links = elements.find_all("a", href=True, string="here")
        return key_regex.search(str(links[0])).group(1)

    @staticmethod
    def _get_ids(link: str) -> str:
        flickr_regex = re.compile(r".*/photos/(?P<user>\d*@\D\d*|\w*)/(?:albums/(?P<album>\d*)|(?P<photo>\d*))")
        try:
            flickr_id = flickr_regex.search(link).group("photo")
            if not flickr_id:
                flickr_id = flickr_regex.search(link).group("album")
            user = flickr_regex.search(link).group("user")
        except AttributeError:
            raise SiteDownloaderError(f"Could not extract Flickr ID from {link}")
        return user, flickr_id

    @staticmethod
    def _construct_direct_link(image_dict: json) -> str:
        image_id = image_dict["photo"]["id"]
        secret = image_dict["photo"]["secret"]
        server = image_dict["photo"]["server"]
        user = image_dict["photo"]["owner"]["nsid"]
        originalsecret = None
        if "originalsecret" in image_dict["photo"]:
            originalsecret = image_dict["photo"]["originalsecret"]
        if "originalformat" in image_dict["photo"]:
            originalformat = image_dict["photo"]["originalformat"]
        if image_dict["photo"]["media"] == "video":
            if originalsecret:
                return Flickr.retrieve_url(
                    f"https://flickr.com/photos/{user}/{image_id}/play/orig/{originalsecret}/",
                ).url
            try:
                return Flickr.retrieve_url(f"https://flickr.com/photos/{user}/{image_id}/play/1080p/{secret}/").url
            except ResourceNotFound:
                try:
                    return Flickr.retrieve_url(f"https://flickr.com/photos/{user}/{image_id}/play/720p/{secret}/").url
                except ResourceNotFound:
                    try:
                        return Flickr.retrieve_url(
                            f"https://flickr.com/photos/{user}/{image_id}/play/360p/{secret}/",
                        ).url
                    except ResourceNotFound:
                        raise SiteDownloaderError("Could not find correct video from Flickr")
        if originalsecret:
            return f"https://live.staticflickr.com/{server}/{image_id}_{originalsecret}_o.{originalformat}"
        return f"https://live.staticflickr.com/{server}/{image_id}_{secret}_b.jpg"

    @staticmethod
    def _get_album_links(album_dict: json, api_string: str) -> list:
        out = []
        for photo in album_dict["photoset"]["photo"]:
            res = Flickr.retrieve_url(f"{api_string}method=flickr.photos.getInfo&photo_id={photo['id']}")
            image_dict = json.loads(res.text)
            out.append(Flickr._construct_direct_link(image_dict))
        return out

    @staticmethod
    def _get_user_id(user: str, api_string: str) -> str:
        try:
            res = Flickr.retrieve_url(
                f"{api_string}method=flickr.urls.lookupUser&url=https://flickr.com/photos/{user}",
            ).text
            return json.loads(res)["user"]["id"]
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f"Could not parse flickr user ID from API: {e}")

    @staticmethod
    def _expand_link(link: str) -> str:
        return Flickr.retrieve_url(link).url

    @staticmethod
    def _get_data(link: str) -> list:
        if ("/gp/" in link) or ("flic.kr" in link):
            link = Flickr._expand_link(link)
        user, flickr_id = Flickr._get_ids(link)
        api_key = Flickr._get_api_key()
        api_string = f"https://www.flickr.com/services/rest/?api_key={api_key}&format=json&nojsoncallback=1&"
        album = False
        if "/albums/" in link:
            if "@" not in user:
                user = Flickr._get_user_id(user, api_string)
            api = f"{api_string}method=flickr.photosets.getPhotos&photoset_id={flickr_id}&user_id={user}"
            album = True
        else:
            api = f"{api_string}method=flickr.photos.getInfo&photo_id={flickr_id}"

        res = Flickr.retrieve_url(api)

        try:
            image_dict = json.loads(res.text)
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f"Could not parse received response as JSON: {e}")

        image_dict = (
            Flickr._get_album_links(image_dict, api_string) if album else [Flickr._construct_direct_link(image_dict)]
        )

        return image_dict
