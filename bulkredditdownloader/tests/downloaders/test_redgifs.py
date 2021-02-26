#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.redgifs import Redgifs


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://www.redgifs.com/watch/forcefulenchantedanaconda',
     'https://thumbs2.redgifs.com/ForcefulEnchantedAnaconda.mp4'),
    ('https://www.redgifs.com/watch/ficklelightirishsetter',
     'https://thumbs2.redgifs.com/FickleLightIrishsetter.mp4'),
))
def test_get_link(test_url: str, expected: str):
    result = Redgifs._get_link(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://www.redgifs.com/watch/forcefulenchantedanaconda', '75a23fff6ddec5de3b61d53db1f265a4'),
    ('https://www.redgifs.com/watch/ficklelightirishsetter', 'd0ea030883c9a3a6a2991f5aa61369e7'),
))
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock
    mock_submission.url = test_url
    test_site = Redgifs(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
