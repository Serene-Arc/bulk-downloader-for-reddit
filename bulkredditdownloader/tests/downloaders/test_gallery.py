#!/usr/bin/env python3
# coding=utf-8

import praw.models
import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.gallery import Gallery


@pytest.fixture()
def reddit_submission(reddit_instance) -> praw.models.Submission:
    return reddit_instance.submission(id='ljyy27')


@pytest.mark.online
@pytest.mark.reddit
def test_gallery(reddit_submission: praw.models.Submission):
    gallery = Gallery(reddit_submission)
    results = gallery.find_resources()
    assert len(results) == 4
    assert all([isinstance(result, Resource) for result in results])
