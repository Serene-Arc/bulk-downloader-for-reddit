#!/usr/bin/env python3
# coding=utf-8

import pytest

from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.site_downloaders.download_factory import DownloadFactory
from bulkredditdownloader.site_downloaders.erome import Erome
from bulkredditdownloader.site_downloaders.gfycat import Gfycat
from bulkredditdownloader.site_downloaders.imgur import Imgur
from bulkredditdownloader.site_downloaders.redgifs import Redgifs


@pytest.mark.parametrize('test_url', ('https://gfycat.com/joyfulpitifulirishterrier',
                                      'https://gfycat.com/blaringaridjellyfish-jensen-ackles-supernatural'))
def test_factory_gfycat(test_url: str):
    result = DownloadFactory.pull_lever(test_url)
    assert result is Gfycat


@pytest.mark.parametrize('test_url', ('https://www.erome.com/a/bbezvaBn',
                                      'https://www.erome.com/a/p14JFlnm'))
def test_factory_erome(test_url):
    result = DownloadFactory.pull_lever(test_url)
    assert result is Erome
