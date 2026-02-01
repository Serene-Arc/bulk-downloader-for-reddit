#!/usr/bin/env python3

import re
import urllib.parse

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.catbox import Catbox
from bdfr.site_downloaders.chevereto import Chevereto
from bdfr.site_downloaders.delay_for_reddit import DelayForReddit
from bdfr.site_downloaders.direct import Direct
from bdfr.site_downloaders.erome import Erome
from bdfr.site_downloaders.fallback_downloaders.ytdlp_fallback import YtdlpFallback
from bdfr.site_downloaders.flickr import Flickr
from bdfr.site_downloaders.gallery import Gallery
from bdfr.site_downloaders.imgchest import Imgchest
from bdfr.site_downloaders.imgur import Imgur
from bdfr.site_downloaders.pornhub import PornHub
from bdfr.site_downloaders.redgifs import Redgifs
from bdfr.site_downloaders.self_post import SelfPost
from bdfr.site_downloaders.vidble import Vidble
from bdfr.site_downloaders.vreddit import VReddit
from bdfr.site_downloaders.youtube import Youtube


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> type[BaseDownloader]:
        sanitised_url = DownloadFactory.sanitise_url(url).lower()
        if re.match(r"(i\.|m\.|o\.)?imgur", sanitised_url):
            return Imgur
        elif re.match(r"(i\.|thumbs\d{1,2}\.|v\d\.)?(redgifs|gifdeliverynetwork)", sanitised_url):
            return Redgifs
        elif re.match(r".*/.*\.[a-zA-Z34]{3,4}(\?[\w;&=]*)?$", sanitised_url) and not DownloadFactory.is_web_resource(
            sanitised_url
        ):
            return Direct
        elif re.match(r"erome\.com.*", sanitised_url):
            return Erome
        elif re.match(r"catbox\.moe", sanitised_url):
            return Catbox
        elif re.match(r"lensdump\.com", sanitised_url) or re.match(r"nsfw\.pics", sanitised_url):
            return Chevereto
        elif re.match(r"delayforreddit\.com", sanitised_url):
            return DelayForReddit
        elif re.match(r"flickr\.com", sanitised_url) or re.match(r"flic\.kr", sanitised_url):
            return Flickr
        elif re.match(r"reddit\.com/gallery/.*", sanitised_url):
            return Gallery
        elif re.match(r"patreon\.com.*", sanitised_url):
            return Gallery
        elif re.match(r"imgchest\.com/p/", sanitised_url):
            return Imgchest
        elif re.match(r"reddit\.com/r/", sanitised_url):
            return SelfPost
        elif re.match(r"(m\.)?youtu\.?be", sanitised_url):
            return Youtube
        elif re.match(r"i\.redd\.it.*", sanitised_url):
            return Direct
        elif re.match(r"v\.redd\.it.*", sanitised_url):
            return VReddit
        elif re.match(r"pornhub\.com.*", sanitised_url):
            return PornHub
        elif re.match(r"vidble\.com", sanitised_url):
            return Vidble
        elif YtdlpFallback.can_handle_link(sanitised_url):
            return YtdlpFallback
        else:
            raise NotADownloadableLinkError(f"No downloader module exists for url {url}")

    @staticmethod
    def sanitise_url(url: str) -> str:
        beginning_regex = re.compile(r"\s*(www\.?)?")
        split_url = urllib.parse.urlsplit(url)
        split_url = split_url.netloc + split_url.path
        split_url = re.sub(beginning_regex, "", split_url)
        return split_url

    @staticmethod
    def is_web_resource(url: str) -> bool:
        web_extensions = (
            "asp",
            "aspx",
            "cfm",
            "cfml",
            "css",
            "htm",
            "html",
            "js",
            "php",
            "php3",
            "xhtml",
        )
        if re.match(rf"(?i).*/.*\.({'|'.join(web_extensions)})$", url):
            return True
        else:
            return False
