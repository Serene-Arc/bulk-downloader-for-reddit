#!/usr/bin/env python3
# coding=utf-8

import pytest

from bulkredditdownloader.resource import Resource


@pytest.mark.parametrize(('test_url', 'expected'), (
    ('test.png', '.png'),
    ('another.mp4', '.mp4'),
    ('test.jpeg', '.jpeg'),
    ('http://www.random.com/resource.png', '.png'),
    ('https://www.resource.com/test/example.jpg', '.jpg'),
    ('hard.png.mp4', '.mp4'),
))
def test_resource_get_extension(test_url: str, expected: str):
    test_resource = Resource(None, test_url)
    result = test_resource._determine_extension()
    assert result == expected
