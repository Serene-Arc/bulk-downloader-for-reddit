#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.vreddit import VReddit


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id'), (
    ('lu8l8g'),
))
def test_find_resources(test_submission_id: str, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    downloader = VReddit(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].content is not None
