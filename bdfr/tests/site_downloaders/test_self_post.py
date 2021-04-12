#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.self_post import SelfPost


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_hash'), (
    ('ltmivt', '7d2c9e4e989e5cf2dca2e55a06b1c4f6'),
    ('ltoaan', '221606386b614d6780c2585a59bd333f'),
    ('d3sc8o', 'c1ff2b6bd3f6b91381dcd18dfc4ca35f'),
))
def test_find_resource(test_submission_id: str, expected_hash: str, reddit_instance: praw.Reddit):
    submission = reddit_instance.submission(id=test_submission_id)
    downloader = SelfPost(submission)
    results = downloader.find_resources()
    assert len(results) == 1
    assert isinstance(results[0], Resource)
    assert results[0].hash.hexdigest() == expected_hash
