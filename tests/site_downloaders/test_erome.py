#!/usr/bin/env python3

import re
from unittest.mock import MagicMock

import pytest

from bdfr.site_downloaders.erome import Erome


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_urls"),
    (("https://www.erome.com/a/vqtPuLXh", (r"https://[a-z]\d+.erome.com/\d{3}/vqtPuLXh/KH2qBT99_480p.mp4",)),),
)
def test_get_link(test_url: str, expected_urls: tuple[str]):
    result = Erome._get_links(test_url)
    assert all([any([re.match(p, r) for r in result]) for p in expected_urls])


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes_len"),
    (
        ("https://www.erome.com/a/vqtPuLXh", 1),  # Video
        ("https://www.erome.com/a/4tP3KI6F", 1),  # Video
        ("https://www.erome.com/a/9E50Xkb6", 10),  # Image album
    ),
)
def test_download_resource(test_url: str, expected_hashes_len: int):
    # Can't compare hashes for this test, Erome doesn't return the exact same file from request to request so the hash
    # will change back and forth randomly
    mock_submission = MagicMock()
    mock_submission.url = test_url
    test_site = Erome(mock_submission)
    resources = test_site.find_resources()
    for res in resources:
        res.download()
    resource_hashes = [res.hash.hexdigest() for res in resources]
    assert len(resource_hashes) == expected_hashes_len
