#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from unittest.mock import Mock

import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader


class BlankDownloader(BaseDownloader):
    def __init__(self, directory, post):
        super().__init__(directory, post)

    def download(self) -> list[Resource]:
        return [self._download_resource(self.post.url)]


@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://docs.python.org/3/_static/py.png', 'a721fc7ec672275e257bbbfde49a4d4e'),
))
def test_get_resource(test_url: str, expected_hash: str):
    mock_submission = Mock
    mock_submission.url = test_url
    downloader = BlankDownloader(Path('.'), mock_submission)
    result = downloader.download()
    assert isinstance(result[0], Resource)
    assert result[0].hash.hexdigest() == expected_hash
