#!/usr/bin/env python3
# coding=utf-8

import re
from typing import Type

from bulkredditdownloader.errors import NotADownloadableLinkError
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.site_downloaders.direct import Direct
from bulkredditdownloader.site_downloaders.erome import Erome
from bulkredditdownloader.site_downloaders.gallery import Gallery
from bulkredditdownloader.site_downloaders.gfycat import Gfycat
from bulkredditdownloader.site_downloaders.imgur import Imgur
from bulkredditdownloader.site_downloaders.redgifs import Redgifs


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> Type[BaseDownloader]:
        url_beginning = r'\s*(https?://(www.)?)'
        if re.match(url_beginning + r'gfycat.com.*', url):
            return Gfycat
        elif re.match(url_beginning + r'erome.com.*', url):
            return Erome
        elif re.match(url_beginning + r'imgur.*', url):
            return Imgur
        elif re.match(url_beginning + r'redgifs.com', url):
            return Redgifs
        elif re.match(url_beginning + r'[vi].redd\.it.*', url):
            return Direct
        elif re.match(url_beginning + r'reddit.com/gallery/.*', url):
            return Gallery
        else:
            raise NotADownloadableLinkError('No downloader module exists for url {}'.format(url))
