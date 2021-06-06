#!/usr/bin/env python3

from unittest.mock import MagicMock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.fallback_downloaders.youtubedl_fallback import YoutubeDlFallback


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://www.reddit.com/r/specializedtools/comments/n2nw5m/bamboo_splitter/', True),
    ('https://www.youtube.com/watch?v=P19nvJOmqCc', True),
    ('https://www.example.com/test', False),
))
def test_can_handle_link(test_url: str, expected: bool):
    result = YoutubeDlFallback.can_handle_link(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://streamable.com/dt46y', '1e7f4928e55de6e3ca23d85cc9246bbb'),
    ('https://streamable.com/t8sem', '49b2d1220c485455548f1edbc05d4ecf'),
    ('https://www.reddit.com/r/specializedtools/comments/n2nw5m/bamboo_splitter/', '21968d3d92161ea5e0abdcaf6311b06c'),
    ('https://v.redd.it/9z1dnk3xr5k61', '351a2b57e888df5ccbc508056511f38d'),
))
def test_find_resources(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = YoutubeDlFallback(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    assert resources[0].hash.hexdigest() == expected_hash
