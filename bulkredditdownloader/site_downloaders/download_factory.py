#!/usr/bin/env python3
# coding=utf-8

import re
from typing import Type

from bulkredditdownloader.exceptions import NotADownloadableLinkError
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.site_downloaders.direct import Direct
from bulkredditdownloader.site_downloaders.erome import Erome
from bulkredditdownloader.site_downloaders.gallery import Gallery
from bulkredditdownloader.site_downloaders.gfycat import Gfycat
from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork
from bulkredditdownloader.site_downloaders.imgur import Imgur
from bulkredditdownloader.site_downloaders.redgifs import Redgifs
from bulkredditdownloader.site_downloaders.self_post import SelfPost
from bulkredditdownloader.site_downloaders.vreddit import VReddit
from bulkredditdownloader.site_downloaders.youtube import Youtube


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> Type[BaseDownloader]:
        url_beginning = r'\s*(https?://(www\.)?)'
        if re.match(url_beginning + r'erome\.com.*', url):
            return Erome
        elif re.match(url_beginning + r'reddit\.com/gallery/.*', url):
            return Gallery
        elif re.match(url_beginning + r'gfycat\.', url):
            return Gfycat
        elif re.match(url_beginning + r'gifdeliverynetwork', url):
            return GifDeliveryNetwork
        elif re.match(url_beginning + r'imgur.*', url):
            return Imgur
        elif re.match(url_beginning + r'i\.imgur.*\.gifv$', url):
            return Imgur
        elif re.match(url_beginning + r'redgifs.com', url):
            return Redgifs
        elif re.match(url_beginning + r'reddit\.com/r/', url):
            return SelfPost
        elif re.match(url_beginning + r'v\.redd\.it', url):
            return VReddit
        elif re.match(url_beginning + r'youtu\.?be', url):
            return Youtube
        elif re.match(url_beginning + r'i\.redd\.it.*', url):
            return Direct
        elif re.match(url_beginning + r'.*\..{3,4}$', url):
            return Direct
        else:
            raise NotADownloadableLinkError('No downloader module exists for url {}'.format(url))
