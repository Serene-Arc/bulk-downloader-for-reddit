#!/usr/bin/env python3

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.vidble import Vidble


@pytest.mark.parametrize(("test_url", "expected"), (("/RDFbznUvcN_med.jpg", "/RDFbznUvcN.jpg"),))
def test_change_med_url(test_url: str, expected: str):
    result = Vidble.change_med_url(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://www.vidble.com/show/UxsvAssYe5",
            {
                "https://www.vidble.com/UxsvAssYe5.gif",
            },
        ),
        (
            "https://vidble.com/show/RDFbznUvcN",
            {
                "https://www.vidble.com/RDFbznUvcN.jpg",
            },
        ),
        (
            "https://vidble.com/album/h0jTLs6B",
            {
                "https://www.vidble.com/XG4eAoJ5JZ.jpg",
                "https://www.vidble.com/IqF5UdH6Uq.jpg",
                "https://www.vidble.com/VWuNsnLJMD.jpg",
                "https://www.vidble.com/sMmM8O650W.jpg",
            },
        ),
        (
            "https://www.vidble.com/pHuwWkOcEb",
            {
                "https://www.vidble.com/pHuwWkOcEb.jpg",
            },
        ),
    ),
)
def test_get_links(test_url: str, expected: set[str]):
    results = Vidble.get_links(test_url)
    assert results == expected


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        (
            "https://www.vidble.com/show/UxsvAssYe5",
            {
                "0ef2f8e0e0b45936d2fb3e6fbdf67e28",
            },
        ),
        (
            "https://vidble.com/show/RDFbznUvcN",
            {
                "c2dd30a71e32369c50eed86f86efff58",
            },
        ),
        (
            "https://vidble.com/album/h0jTLs6B",
            {
                "3b3cba02e01c91f9858a95240b942c71",
                "dd6ecf5fc9e936f9fb614eb6a0537f99",
                "b31a942cd8cdda218ed547bbc04c3a27",
                "6f77c570b451eef4222804bd52267481",
            },
        ),
        (
            "https://www.vidble.com/pHuwWkOcEb",
            {
                "585f486dd0b2f23a57bddbd5bf185bc7",
            },
        ),
    ),
)
def test_find_resources(test_url: str, expected_hashes: set[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Vidble(mock_download)
    results = downloader.find_resources()
    assert all([isinstance(res, Resource) for res in results])
    [res.download() for res in results]
    hashes = set([res.hash.hexdigest() for res in results])
    assert hashes == set(expected_hashes)
