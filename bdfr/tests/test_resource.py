#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.resource import Resource


@pytest.mark.parametrize(('test_url', 'expected'), (
    ('test.png', '.png'),
    ('another.mp4', '.mp4'),
    ('test.jpeg', '.jpeg'),
    ('http://www.random.com/resource.png', '.png'),
    ('https://www.resource.com/test/example.jpg', '.jpg'),
    ('hard.png.mp4', '.mp4'),
    ('https://preview.redd.it/7zkmr1wqqih61.png?width=237&format=png&auto=webp&s=19de214e634cbcad99', '.png'),
    ('test.jpg#test', '.jpg'),
    ('test.jpg?width=247#test', '.jpg'),
    ('https://www.test.com/test/test2/example.png?random=test#thing', '.png'),
))
def test_resource_get_extension(test_url: str, expected: str):
    test_resource = Resource(MagicMock(), test_url)
    result = test_resource._determine_extension()
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://www.iana.org/_img/2013.1/iana-logo-header.svg', '426b3ac01d3584c820f3b7f5985d6623'),
))
def test_download_online_resource(test_url: str, expected_hash: str):
    test_resource = Resource(MagicMock(), test_url)
    test_resource.download(120)
    assert test_resource.hash.hexdigest() == expected_hash
