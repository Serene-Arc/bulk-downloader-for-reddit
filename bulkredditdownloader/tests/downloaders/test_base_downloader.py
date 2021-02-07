#!/uasr/bin/env python3
# coding=utf-8

from pathlib import Path

import pytest

from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader


@pytest.mark.parametrize(('test_bytes', 'expected'), ((b'test', '098f6bcd4621d373cade4e832627b4f6'),
                                                      (b'test2', 'ad0234829205b9033196ba818f7a872b')))
def test_create_hash(test_bytes: bytes, expected: str):
    result = BaseDownloader._create_hash(test_bytes)
    assert result == expected


@pytest.mark.parametrize(('test_url', 'expected'), (('test.png', '.png'),
                                                    ('random.jpg', '.jpg'),
                                                    ('http://random.com/test.png', '.png'),
                                                    ('https://example.net/picture.jpg', '.jpg'),
                                                    ('https://v.redd.it/picture', '.mp4'),
                                                    ('https://v.redd.it/picture.jpg', '.jpg'),
                                                    ('https:/random.url', '.jpg')
                                                    ))
def test_get_extension(test_url: str, expected: str):
    result = BaseDownloader._get_extension(test_url)
    assert result == expected


@pytest.mark.skip
@pytest.mark.parametrize(('test_url', 'expected_hash'), (('https://www.iana.org/_img/2013.1/iana-logo-header.svg', ''),
                                                         ('', '')
                                                         ))
def test_download_resource(test_url: str, expected_hash: str, tmp_path: Path):
    test_file = tmp_path / 'test'
    BaseDownloader._download_resource(test_file, tmp_path, test_url)
    assert test_file.exists()
    with open(test_file, 'rb') as file:
        content = file.read()
    hash_result = BaseDownloader._create_hash(content)
    assert hash_result == expected_hash
