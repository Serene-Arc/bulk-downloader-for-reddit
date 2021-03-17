#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.gallery import Gallery


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_len'), (
    ('ljyy27', 4),
    ('m6lvrh', 4),
))
def test_gallery(test_submission_id: str, expected_len: int, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    gallery = Gallery(test_submission)
    results = gallery.find_resources()
    assert len(results) == expected_len
    assert all([isinstance(result, Resource) for result in results])
