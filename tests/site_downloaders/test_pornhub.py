#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.pornhub import PornHub


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://www.pornhub.com/view_video.php?viewkey=ph5a2ee0461a8d0', '5f5294b9b97dbb7cb9cf8df278515621'),
))
def test_find_resources_good(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = PornHub(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].hash.hexdigest() == expected_hash
