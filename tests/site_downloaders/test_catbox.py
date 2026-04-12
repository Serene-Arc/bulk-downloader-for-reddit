from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.catbox import Catbox


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://catbox.moe/c/vel5eg",
            {
                "https://files.catbox.moe/h2dx9k.gif",
                "https://files.catbox.moe/bc83lg.png",
                "https://files.catbox.moe/aq3m2a.jpeg",
                "https://files.catbox.moe/yfk8r7.jpeg",
                "https://files.catbox.moe/34ofbz.png",
                "https://files.catbox.moe/xx4lcw.mp4",
                "https://files.catbox.moe/xocd6t.mp3",
            },
        ),
    ),
)
def test_get_links(test_url: str, expected: set[str]):
    results = Catbox.get_links(test_url)
    assert results == expected


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        (
            "https://catbox.moe/c/vel5eg",
            {
                "014762b38e280ef3c0d000cc5f2aa386",
                "85799edf12e20876f37286784460ad1b",
                "c71b88c4230aa3aaad52a644fb709737",
                "f40cffededd1929726d9cd265cc42c67",
                "bda1f646c49607183c2450441f2ea6e8",
                "21b48729bf9be7884999442b73887eed",
                "0ec327259733a8276c207cc6e1b001ad",
            },
        ),
    ),
)
def test_download_resources(test_url: str, expected_hashes: set[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Catbox(mock_download)
    results = downloader.find_resources()
    assert all(isinstance(res, Resource) for res in results)
    [res.download() for res in results]
    hashes = {res.hash.hexdigest() for res in results}
    assert hashes == set(expected_hashes)
