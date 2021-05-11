#!/usr/bin/env python3
# coding=utf-8

import re
import urllib.parse
from typing import Type

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.direct import Direct
from bdfr.site_downloaders.erome import Erome
from bdfr.site_downloaders.fallback_downloaders.youtubedl_fallback import YoutubeDlFallback
from bdfr.site_downloaders.gallery import Gallery
from bdfr.site_downloaders.gfycat import Gfycat
from bdfr.site_downloaders.imgur import Imgur
from bdfr.site_downloaders.redgifs import Redgifs
from bdfr.site_downloaders.self_post import SelfPost
from bdfr.site_downloaders.youtube import Youtube


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> Type[BaseDownloader]:
        sanitised_url = DownloadFactory._sanitise_url(url)
        if re.match(r'(i\.)?imgur.*\.gifv$', sanitised_url):
            return Imgur
        elif re.match(r'.*/.*\.\w{3,4}(\?[\w;&=]*)?$', sanitised_url):
            return Direct
        elif re.match(r'erome\.com.*', sanitised_url):
            return Erome
        elif re.match(r'reddit\.com/gallery/.*', sanitised_url):
            return Gallery
        elif re.match(r'gfycat\.', sanitised_url):
            return Gfycat
        elif re.match(r'(m\.)?imgur.*', sanitised_url):
            return Imgur
        elif re.match(r'(redgifs|gifdeliverynetwork)', sanitised_url):
            return Redgifs
        elif re.match(r'reddit\.com/r/', sanitised_url):
            return SelfPost
        elif re.match(r'(m\.)?youtu\.?be', sanitised_url):
            return Youtube
        elif re.match(r'i\.redd\.it.*', sanitised_url):
            return Direct
        elif YoutubeDlFallback.can_handle_link(sanitised_url):
            return YoutubeDlFallback
        else:
            raise NotADownloadableLinkError(
                f'No downloader module exists for url {url}')

    @staticmethod
    def _sanitise_url(url: str) -> str:
        beginning_regex = re.compile(r'\s*(www\.?)?')
        split_url = urllib.parse.urlsplit(url)
        split_url = split_url.netloc + split_url.path
        split_url = re.sub(beginning_regex, '', split_url)
        return split_url
