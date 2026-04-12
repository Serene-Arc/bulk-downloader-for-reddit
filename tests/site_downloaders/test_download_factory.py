#!/usr/bin/env python3

import praw
import pytest

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.direct import Direct
from bdfr.site_downloaders.download_factory import DownloadFactory
from bdfr.site_downloaders.erome import Erome
from bdfr.site_downloaders.fallback_downloaders.ytdlp_fallback import YtdlpFallback
from bdfr.site_downloaders.gallery import Gallery
from bdfr.site_downloaders.imgur import Imgur
from bdfr.site_downloaders.pornhub import PornHub
from bdfr.site_downloaders.redgifs import Redgifs
from bdfr.site_downloaders.self_post import SelfPost
from bdfr.site_downloaders.vreddit import VReddit
from bdfr.site_downloaders.youtube import Youtube


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_submission_url", "expected_class"),
    (
        (
            "https://www.reddit.com/r/TwoXChromosomes/comments/lu29zn/i_refuse_to_live_my_life"
            "_in_anything_but_comfort/",
            SelfPost,
        ),
        ("https://i.redd.it/affyv0axd5k61.png", Direct),
        ("https://i.imgur.com/bZx1SJQ.jpg", Imgur),
        ("https://i.Imgur.com/bZx1SJQ.jpg", Imgur),
        ("https://imgur.com/BuzvZwb.gifv", Imgur),
        ("https://imgur.com/a/MkxAzeg", Imgur),
        ("https://m.imgur.com/a/py3RW0j", Imgur),
        ("https://www.reddit.com/gallery/lu93m7", Gallery),
        ("https://www.erome.com/a/NWGw0F09", Erome),
        ("https://youtube.com/watch?v=Gv8Wz74FjVA", Youtube),
        ("https://redgifs.com/watch/courageousimpeccablecanvasback", Redgifs),
        ("https://www.gifdeliverynetwork.com/repulsivefinishedandalusianhorse", Redgifs),
        ("https://thumbs4.redgifs.com/DismalIgnorantDrongo-mobile.mp4", Redgifs),
        ("https://v3.redgifs.com/watch/kaleidoscopicdaringvenomoussnake", Redgifs),
        ("https://youtu.be/DevfjHOhuFc", Youtube),
        ("https://m.youtube.com/watch?v=kr-FeojxzUM", Youtube),
        ("https://dynasty-scans.com/system/images_images/000/017/819/original/80215103_p0.png?1612232781", Direct),
        ("https://v.redd.it/9z1dnk3xr5k61", VReddit),
        ("https://streamable.com/dt46y", YtdlpFallback),
        ("https://vimeo.com/channels/31259/53576664", YtdlpFallback),
        ("http://video.pbs.org/viralplayer/2365173446/", YtdlpFallback),
        ("https://www.pornhub.com/view_video.php?viewkey=ph5a2ee0461a8d0", PornHub),
        ("https://www.patreon.com/posts/minecart-track-59346560", Gallery),
    ),
)
def test_factory_lever_good(test_submission_url: str, expected_class: BaseDownloader, reddit_instance: praw.Reddit):
    result = DownloadFactory.pull_lever(test_submission_url)
    assert result is expected_class


@pytest.mark.parametrize(
    "test_url",
    (
        "random.com",
        "bad",
        "https://www.google.com/",
        "https://www.google.com",
        "https://www.google.com/test",
        "https://www.google.com/test/",
        "https://www.tiktok.com/@keriberry.420",
    ),
)
def test_factory_lever_bad(test_url: str):
    with pytest.raises(NotADownloadableLinkError):
        DownloadFactory.pull_lever(test_url)


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("www.test.com/test.png", "test.com/test.png"),
        ("www.test.com/test.png?test_value=random", "test.com/test.png"),
        ("https://youtube.com/watch?v=Gv8Wz74FjVA", "youtube.com/watch"),
        ("https://i.imgur.com/BuzvZwb.gifv", "i.imgur.com/BuzvZwb.gifv"),
    ),
)
def test_sanitise_url(test_url: str, expected: str):
    result = DownloadFactory.sanitise_url(test_url)
    assert result == expected


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("www.example.com/test.asp", True),
        ("www.example.com/test.html", True),
        ("www.example.com/test.js", True),
        ("www.example.com/test.xhtml", True),
        ("www.example.com/test.mp4", False),
        ("www.example.com/test.png", False),
    ),
)
def test_is_web_resource(test_url: str, expected: bool):
    result = DownloadFactory.is_web_resource(test_url)
    assert result == expected
