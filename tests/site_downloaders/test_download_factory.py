#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.direct import Direct
from bdfr.site_downloaders.download_factory import DownloadFactory
from bdfr.site_downloaders.erome import Erome
from bdfr.site_downloaders.fallback_downloaders.youtubedl_fallback import YoutubeDlFallback
from bdfr.site_downloaders.gallery import Gallery
from bdfr.site_downloaders.gfycat import Gfycat
from bdfr.site_downloaders.imgur import Imgur
from bdfr.site_downloaders.redgifs import Redgifs
from bdfr.site_downloaders.self_post import SelfPost
from bdfr.site_downloaders.youtube import Youtube


@pytest.mark.online
@pytest.mark.parametrize(('test_submission_url', 'expected_class'), (
    ('https://www.reddit.com/r/TwoXChromosomes/comments/lu29zn/i_refuse_to_live_my_life'
     '_in_anything_but_comfort/', SelfPost),
    ('https://i.imgur.com/bZx1SJQ.jpg', Direct),
    ('https://i.redd.it/affyv0axd5k61.png', Direct),
    ('https://imgur.com/3ls94yv.jpeg', Direct),
    ('https://i.imgur.com/BuzvZwb.gifv', Imgur),
    ('https://imgur.com/BuzvZwb.gifv', Imgur),
    ('https://i.imgur.com/6fNdLst.gif', Direct),
    ('https://imgur.com/a/MkxAzeg', Imgur),
    ('https://www.reddit.com/gallery/lu93m7', Gallery),
    ('https://gfycat.com/concretecheerfulfinwhale', Gfycat),
    ('https://www.erome.com/a/NWGw0F09', Erome),
    ('https://youtube.com/watch?v=Gv8Wz74FjVA', Youtube),
    ('https://redgifs.com/watch/courageousimpeccablecanvasback', Redgifs),
    ('https://www.gifdeliverynetwork.com/repulsivefinishedandalusianhorse', Redgifs),
    ('https://youtu.be/DevfjHOhuFc', Youtube),
    ('https://m.youtube.com/watch?v=kr-FeojxzUM', Youtube),
    ('https://i.imgur.com/3SKrQfK.jpg?1', Direct),
    ('https://dynasty-scans.com/system/images_images/000/017/819/original/80215103_p0.png?1612232781', Direct),
    ('https://m.imgur.com/a/py3RW0j', Imgur),
    ('https://v.redd.it/9z1dnk3xr5k61', YoutubeDlFallback),
    ('https://streamable.com/dt46y', YoutubeDlFallback),
    ('https://vimeo.com/channels/31259/53576664', YoutubeDlFallback),
    ('http://video.pbs.org/viralplayer/2365173446/', YoutubeDlFallback),
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


@pytest.mark.parametrize(('test_url', 'expected'), (
    ('www.test.com/test.png', 'test.com/test.png'),
    ('www.test.com/test.png?test_value=random', 'test.com/test.png'),
    ('https://youtube.com/watch?v=Gv8Wz74FjVA', 'youtube.com/watch'),
    ('https://i.imgur.com/BuzvZwb.gifv', 'i.imgur.com/BuzvZwb.gifv'),
))
def test_sanitise_urll(test_url: str, expected: str):
    result = DownloadFactory._sanitise_url(test_url)
    assert result == expected
