#!/usr/bin/env python3

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.imgur import Imgur


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("https://imgur.com/a/xWZsDDP", "xWZsDDP"),  # Gallery, /a/
        ("https://imgur.com/gallery/IjJJdlC", "IjJJdlC"),  # Gallery, /gallery/
        ("https://imgur.com/gallery/IjJJdlC/", "IjJJdlC"),  # Gallery, trailing /
        ("https://o.imgur.com/jZw9gq2.jpg", "jZw9gq2"),  # Direct link, jpg, incorrect subdomain
        ("https://i.imgur.com/lFJai6i.gifv", "lFJai6i"),  # Direct link, gifv
        ("https://i.imgur.com/ywSyILa.gifv?", "ywSyILa"),  # Direct link, gifv, trailing ?
        ("https://imgur.com/ubYwpbk.GIFV", "ubYwpbk"),  # No subdomain, uppercase gifv
        ("https://i.imgur.com/OGeVuAe.giff", "OGeVuAe"),  # Direct link, incorrect extension
        ("https://i.imgur.com/OGeVuAe.gift", "OGeVuAe"),  # Direct link, incorrect extension
        ("https://i.imgur.com/3SKrQfK.jpg?1", "3SKrQfK"),  # Direct link, trainling ?1
        ("https://i.imgur.com/cbivYRW.jpg?3", "cbivYRW"),  # Direct link, trailing ?3
        ("http://i.imgur.com/s9uXxlq.jpg?5.jpg", "s9uXxlq"),  # Direct link, trailing ?5.jpg, http
        ("http://i.imgur.com/s9uXxlqb.jpg", "s9uXxlqb"),  # Direct link, jpg, http
        ("https://i.imgur.com/2TtN68l_d.webp", "2TtN68l"),  # Direct link, webp, _d thumbnail
        ("https://imgur.com/a/1qzfWtY/gifv", "1qzfWtY"),  # Gallery, trailing filetype
        ("https://imgur.com/a/1qzfWtY/spqr", "1qzfWtY"),  # Gallery, trailing non filetype
    ),
)
def test_get_id(test_url: str, expected: str):
    result = Imgur._get_id(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        ("https://imgur.com/a/xWZsDDP", ("f551d6e6b0fef2ce909767338612e31b",)),  # Single image gallery
        ("https://imgur.com/gallery/IjJJdlC", ("740b006cf9ec9d6f734b6e8f5130bdab",)),  # Single video gallery
        (
            "https://imgur.com/a/dcc84Gt",  # Multiple image gallery
            (
                "cf1158e1de5c3c8993461383b96610cf",
                "28d6b791a2daef8aa363bf5a3198535d",
                "248ef8f2a6d03eeb2a80d0123dbaf9b6",
                "029c475ce01b58fdf1269d8771d33913",
            ),
        ),
        ("https://i.imgur.com/j1CNCZY.gifv", ("ed63d7062bc32edaeea8b53f876a307c",)),  # Direct video link
        ("https://i.imgur.com/uTvtQsw.gifv", ("46c86533aa60fc0e09f2a758513e3ac2",)),  # Direct video link
        (
            "https://i.imgur.com/OGeVuAe.giff",  # Direct video link, incorrect extension
            ("77389679084d381336f168538793f218",),
        ),
        ("https://i.imgur.com/cbivYRW.jpg?3", ("7ec6ceef5380cb163a1d498c359c51fd",)),  # Direct image link, trailing ?3
        (
            "http://i.imgur.com/s9uXxlq.jpg?5.jpg",  # Direct image link, trailing ?5.jpg
            ("338de3c23ee21af056b3a7c154e2478f",),
        ),
        ("http://i.imgur.com/s9uXxlqb.jpg", ("338de3c23ee21af056b3a7c154e2478f",)),  # Direct image link
        (
            "https://imgur.com/a/1qzfWtY/mp4",  # Single video gallery, web filetype request
            ("65fbc7ba5c3ed0e3af47c4feef4d3735",),
        ),
        (
            "https://imgur.com/a/1qzfWtY/spqr",  # Single video gallery, web filetype invalid
            ("65fbc7ba5c3ed0e3af47c4feef4d3735",),
        ),
    ),
)
def test_find_resources(test_url: str, expected_hashes: list[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Imgur(mock_download)
    results = downloader.find_resources()
    assert all([isinstance(res, Resource) for res in results])
    [res.download() for res in results]
    hashes = set([res.hash.hexdigest() for res in results])
    assert hashes == set(expected_hashes)
