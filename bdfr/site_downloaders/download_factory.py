#!/usr/bin/env python3
# coding=utf-8

import re
from typing import Type

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.direct import Direct
from bdfr.site_downloaders.erome import Erome
from bdfr.site_downloaders.gallery import Gallery
from bdfr.site_downloaders.gfycat import Gfycat
from bdfr.site_downloaders.gif_delivery_network import GifDeliveryNetwork
from bdfr.site_downloaders.imgur import Imgur
from bdfr.site_downloaders.redgifs import Redgifs
from bdfr.site_downloaders.self_post import SelfPost
from bdfr.site_downloaders.vreddit import VReddit
from bdfr.site_downloaders.youtube import Youtube


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> Type[BaseDownloader]:
        url_beginning = r'\s*(https?://(www\.)?)'
        if re.match(url_beginning + r'(i\.)?imgur.*\.gifv$', url):
            return Imgur
        elif re.match(url_beginning + r'.*/.*\.\w{3,4}(\?[\w;&=]*)?$', url):
            return Direct
        elif re.match(url_beginning + r'erome\.com.*', url):
            return Erome
        elif re.match(url_beginning + r'reddit\.com/gallery/.*', url):
            return Gallery
        elif re.match(url_beginning + r'gfycat\.', url):
            return Gfycat
        elif re.match(url_beginning + r'gifdeliverynetwork', url):
            return GifDeliveryNetwork
        elif re.match(url_beginning + r'(m\.)?imgur.*', url):
            return Imgur
        elif re.match(url_beginning + r'redgifs.com', url):
            return Redgifs
        elif re.match(url_beginning + r'reddit\.com/r/', url):
            return SelfPost
        elif re.match(url_beginning + r'v\.redd\.it', url):
            return VReddit
        elif re.match(url_beginning + r'(m\.)?youtu\.?be', url):
            return Youtube
        elif re.match(url_beginning + r'i\.redd\.it.*', url):
            return Direct
        else:
            raise NotADownloadableLinkError(f'No downloader module exists for url {url}')
