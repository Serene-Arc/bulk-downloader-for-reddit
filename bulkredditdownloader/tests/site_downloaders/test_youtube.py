#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.youtube import Youtube


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://www.youtube.com/watch?v=uSm2VDgRIUs', '3c79a62898028987f94161e0abccbddf'),
    ('https://www.youtube.com/watch?v=m-tKnjFwleU', '30314930d853afff8ebc7d8c36a5b833'),
))
def test_find_resources(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = Youtube(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
