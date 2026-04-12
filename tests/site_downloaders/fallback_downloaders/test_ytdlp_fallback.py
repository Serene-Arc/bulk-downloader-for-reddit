#!/usr/bin/env python3

from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.resource import Resource
from bdfr.site_downloaders.fallback_downloaders.ytdlp_fallback import YtdlpFallback


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("https://www.reddit.com/r/specializedtools/comments/n2nw5m/bamboo_splitter/", True),
        ("https://www.youtube.com/watch?v=DWUbA501CO4", True),
        ("https://www.example.com/test", False),
        ("https://milesmatrix.bandcamp.com/album/la-boum/", False),
        ("https://v.redd.it/dlr54z8p182a1", True),
    ),
)
def test_can_handle_link(test_url: str, expected: bool):
    result = YtdlpFallback.can_handle_link(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize("test_url", ("https://milesmatrix.bandcamp.com/album/la-boum/",))
def test_info_extraction_bad(test_url: str):
    with pytest.raises(NotADownloadableLinkError):
        YtdlpFallback.get_video_attributes(test_url)


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (
        ("https://streamable.com/dt46y", "b7e465adaade5f2b6d8c2b4b7d0a2878"),
        ("https://streamable.com/t8sem", "49b2d1220c485455548f1edbc05d4ecf"),
        (
            "https://www.reddit.com/r/specializedtools/comments/n2nw5m/bamboo_splitter/",
            "6c6ff46e04b4e33a755ae2a9b5a45ac5",
        ),
        ("https://v.redd.it/9z1dnk3xr5k61", "226cee353421c7aefb05c92424cc8cdd"),
    ),
)
def test_find_resources(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = YtdlpFallback(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    for res in resources:
        res.download()
    assert resources[0].hash.hexdigest() == expected_hash
