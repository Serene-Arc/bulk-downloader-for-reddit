#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import NotADownloadableLinkError
from bdfr.resource import Resource
from bdfr.site_downloaders.youtube import Youtube


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (
        ("https://www.youtube.com/watch?v=_-1E_U0JQkc", "236f01090d5bbb246422df417f388cde"),
        ("https://www.youtube.com/watch?v=_6-UUisQczE", "12f7f30feae276c9fe1039a8266a3a8e"),
    ),
)
def test_find_resources_good(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = Youtube(test_submission)
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
    downloader = Youtube(test_submission)
    with pytest.raises(NotADownloadableLinkError):
        downloader.find_resources()
