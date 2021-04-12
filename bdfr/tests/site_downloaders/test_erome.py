#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.site_downloaders.erome import Erome


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_urls'), (
    ('https://www.erome.com/a/vqtPuLXh', (
        'https://s11.erome.com/365/vqtPuLXh/KH2qBT99_480p.mp4',
    )),
    ('https://www.erome.com/a/ORhX0FZz', (
        'https://s4.erome.com/355/ORhX0FZz/9IYQocM9_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/9eEDc8xm_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/EvApC7Rp_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/LruobtMs_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/TJNmSUU5_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/X11Skh6Z_480p.mp4',
        'https://s4.erome.com/355/ORhX0FZz/bjlTkpn7_480p.mp4'
    )),
))
def test_get_link(test_url: str, expected_urls: tuple[str]):
    result = Erome. _get_links(test_url)
    assert set(result) == set(expected_urls)


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_hashes'), (
    ('https://www.erome.com/a/vqtPuLXh', {
        '5da2a8d60d87bed279431fdec8e7d72f'
    }),
    ('https://www.erome.com/i/ItASD33e', {
        'b0d73fedc9ce6995c2f2c4fdb6f11eff'
    }),
    ('https://www.erome.com/a/lGrcFxmb', {
        '0e98f9f527a911dcedde4f846bb5b69f',
        '25696ae364750a5303fc7d7dc78b35c1',
        '63775689f438bd393cde7db6d46187de',
        'a1abf398cfd4ef9cfaf093ceb10c746a',
        'bd9e1a4ea5ef0d6ba47fb90e337c2d14'
    }),
))
def test_download_resource(test_url: str, expected_hashes: tuple[str]):
    # Can't compare hashes for this test, Erome doesn't return the exact same file from request to request so the hash
    # will change back and forth randomly
    mock_submission = MagicMock()
    mock_submission.url = test_url
    test_site = Erome(mock_submission)
    resources = test_site.find_resources()
    [res.download(120) for res in resources]
    resource_hashes = [res.hash.hexdigest() for res in resources]
    assert len(resource_hashes) == len(expected_hashes)
