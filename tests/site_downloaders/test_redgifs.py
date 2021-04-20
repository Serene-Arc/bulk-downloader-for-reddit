#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.redgifs import Redgifs


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://redgifs.com/watch/frighteningvictorioussalamander',
     'https://thumbs2.redgifs.com/FrighteningVictoriousSalamander.mp4'),
    ('https://redgifs.com/watch/springgreendecisivetaruca',
     'https://thumbs2.redgifs.com/SpringgreenDecisiveTaruca.mp4'),
))
def test_get_link(test_url: str, expected: str):
    result = Redgifs._get_link(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://redgifs.com/watch/frighteningvictorioussalamander', '4007c35d9e1f4b67091b5f12cffda00a'),
    ('https://redgifs.com/watch/springgreendecisivetaruca', '8dac487ac49a1f18cc1b4dabe23f0869'),
))
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Redgifs(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].hash.hexdigest() == expected_hash
