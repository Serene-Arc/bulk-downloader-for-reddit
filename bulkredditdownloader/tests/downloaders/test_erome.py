#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.erome import Erome


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_urls'), (
    ('https://www.erome.com/a/hzLCb2c5',
     ('https://s2.erome.com/353/hzLCb2c5/8FNh4qa8.jpg', 'https://s2.erome.com/353/hzLCb2c5/8FNh4qa8_480p.mp4')
     ),
    ('https://www.erome.com/a/ORhX0FZz',
     ('https://s4.erome.com/355/ORhX0FZz/9IYQocM9.jpg',
      'https://s4.erome.com/355/ORhX0FZz/9IYQocM9_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/9eEDc8xm.jpg',
      'https://s4.erome.com/355/ORhX0FZz/9eEDc8xm_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/EvApC7Rp.jpg',
      'https://s4.erome.com/355/ORhX0FZz/EvApC7Rp_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/LruobtMs.jpg',
      'https://s4.erome.com/355/ORhX0FZz/LruobtMs_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/TJNmSUU5.jpg',
      'https://s4.erome.com/355/ORhX0FZz/TJNmSUU5_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/X11Skh6Z.jpg',
      'https://s4.erome.com/355/ORhX0FZz/X11Skh6Z_480p.mp4',
      'https://s4.erome.com/355/ORhX0FZz/bjlTkpn7.jpg',
      'https://s4.erome.com/355/ORhX0FZz/bjlTkpn7_480p.mp4')
     ),
))
def test_get_link(test_url: str, expected_urls: tuple[str]):
    result = Erome. _get_links(test_url)
    assert set(result) == set(expected_urls)


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_number_of_resources', 'expected_hashes'), (
    ('https://www.erome.com/a/hzLCb2c5', 2,
     ('1b4b1703f81f2ad6a622f7319a4651c2', 'f24388a0f3443c1a27594e4af41c3e83')
     ),
))
def test_download_resource(test_url: str, expected_number_of_resources: int, expected_hashes: tuple[str]):
    mock_submission = Mock
    mock_submission.url = test_url
    test_site = Erome(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == expected_number_of_resources
    [res.download() for res in resources]
    resource_hashes = [res.hash.hexdigest() for res in resources]
    assert set(resource_hashes) == set(expected_hashes)
