#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.gallery import Gallery


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://www.reddit.com/gallery/m6lvrh', {
        'https://preview.redd.it/18nzv9ch0hn61.jpg',
        'https://preview.redd.it/jqkizcch0hn61.jpg',
        'https://preview.redd.it/k0fnqzbh0hn61.jpg',
        'https://preview.redd.it/m3gamzbh0hn61.jpg'
    }),
    ('https://www.reddit.com/gallery/ljyy27', {
        'https://preview.redd.it/04vxj25uqih61.png',
        'https://preview.redd.it/0fnx83kpqih61.png',
        'https://preview.redd.it/7zkmr1wqqih61.png',
        'https://preview.redd.it/u37k5gxrqih61.png'
    }),
))
def test_gallery_get_links(test_url: str, expected: set[str]):
    results = Gallery._get_links(test_url)
    assert set(results) == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_len'), (
    ('m6lvrh', 4),
    ('ljyy27', 4),
))
def test_gallery(test_submission_id: str, expected_len: int, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    gallery = Gallery(test_submission)
    results = gallery.find_resources()
    assert len(results) == expected_len
    assert all([isinstance(result, Resource) for result in results])
