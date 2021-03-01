#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.vreddit import VReddit


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_hash'), (
    ('lu8l8g', '93a15642d2f364ae39f00c6d1be354ff'),
))
def test_find_resources(test_submission_id: str, expected_hash: str, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    downloader = VReddit(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
