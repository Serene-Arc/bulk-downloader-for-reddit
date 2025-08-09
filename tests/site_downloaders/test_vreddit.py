#!/usr/bin/env python3

from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.resource import Resource
from bdfr.site_downloaders.vreddit import VReddit


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (("https://reddit.com/r/Unexpected/comments/z4xsuj/omg_thats_so_cute/", "1ffab5e5c0cc96db18108e4f37e8ca7f"),),
)
def test_find_resources_good(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = VReddit(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash


@pytest.mark.online
@pytest.mark.parametrize(
    "test_url",
    (
        "https://www.polygon.com/disney-plus/2020/5/14/21249881/gargoyles-animated-series-disney-plus-greg-weisman"
        "-interview-oj-simpson-goliath-chronicles",
    ),
)
def test_find_resources_bad(test_url: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = VReddit(test_submission)
    with pytest.raises(NotADownloadableLinkError):
        downloader.find_resources()
