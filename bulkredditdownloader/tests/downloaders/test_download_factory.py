#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bulkredditdownloader.exceptions import NotADownloadableLinkError
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.site_downloaders.direct import Direct
from bulkredditdownloader.site_downloaders.download_factory import DownloadFactory
from bulkredditdownloader.site_downloaders.erome import Erome
from bulkredditdownloader.site_downloaders.gallery import Gallery
from bulkredditdownloader.site_downloaders.gfycat import Gfycat
from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork
from bulkredditdownloader.site_downloaders.imgur import Imgur
from bulkredditdownloader.site_downloaders.redgifs import Redgifs
from bulkredditdownloader.site_downloaders.self_post import SelfPost
from bulkredditdownloader.site_downloaders.vreddit import VReddit
from bulkredditdownloader.site_downloaders.youtube import Youtube


@pytest.mark.parametrize(('test_submission_url', 'expected_class'), (
    ('https://v.redd.it/9z1dnk3xr5k61', VReddit),
    ('https://www.reddit.com/r/TwoXChromosomes/comments/lu29zn/i_refuse_to_live_my_life_in_anything_but_comfort/', SelfPost),
    ('https://i.imgur.com/bZx1SJQ.jpg', Direct),
    ('https://i.redd.it/affyv0axd5k61.png', Direct),
    ('https://i.imgur.com/BuzvZwb.gifv', Imgur),
    ('https://i.imgur.com/6fNdLst.gif', Direct),
    ('https://imgur.com/a/MkxAzeg', Imgur),
    ('https://www.reddit.com/gallery/lu93m7', Gallery),
    ('https://gfycat.com/concretecheerfulfinwhale', Gfycat),
    ('https://www.erome.com/a/NWGw0F09', Erome),
    ('https://youtube.com/watch?v=Gv8Wz74FjVA', Youtube),
    ('https://redgifs.com/watch/courageousimpeccablecanvasback', Redgifs),
    ('https://www.gifdeliverynetwork.com/repulsivefinishedandalusianhorse', GifDeliveryNetwork),
    ('https://youtu.be/DevfjHOhuFc', Youtube),
))
def test_factory_lever_good(test_submission_url: str, expected_class: BaseDownloader, reddit_instance: praw.Reddit):
    result = DownloadFactory.pull_lever(test_submission_url)
    assert result is expected_class


@pytest.mark.parametrize('test_url', (
    'random.com',
    'bad',
    'https://www.google.com/',
    'https://www.google.com',
    'https://www.google.com/test',
    'https://www.google.com/test/',
))
def test_factory_lever_bad(test_url: str):
    with pytest.raises(NotADownloadableLinkError):
        DownloadFactory.pull_lever(test_url)
