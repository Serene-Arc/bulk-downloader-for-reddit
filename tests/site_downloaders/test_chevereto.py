from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.chevereto import Chevereto


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://lensdump.com/a/Vb411",  # Album
            {
                "https://i3.lensdump.com/i/CDIUci.gif?open=true",
                "https://i.lensdump.com/i/CDIXZo.jpeg?open=true",
                "https://i1.lensdump.com/i/CDIwD2.jpeg?open=true",
                "https://i3.lensdump.com/i/CDI5VC.gif?open=true",
                "https://i1.lensdump.com/i/CDIGn5.jpeg?open=true",
            },
        ),
        (
            "https://lensdump.com/i/CDIUci",  # Single image
            {"https://i3.lensdump.com/i/CDIUci.gif?open=true"},
        ),
        (
            "https://lensdump.com/a/Vb411",  # Album
            {
                "https://lensdump.com/i/CDIUci",
                "https://lensdump.com/i/CDIXZo",
                "https://lensdump.com/i/CDIwD2",
                "https://lensdump.com/i/CDI5VC",
                "https://lensdump.com/i/CDIGn5",
            },
        ),
    ),
)
def test_get_links(test_url: str, expected: set[str]):
    results = Chevereto._get_links(test_url)
    assert sorted(results) == sorted(expected)


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        (
            "https://nsfw.pics/album/Test.l2t",  # Album
            {
                "9ceac1e26c4799b0a6b7d5453a73f53b",
                "8ff9229c39ad5403e9859a21d5aec103",
                "907f92b1c295d5f84f4f64aacc960079",
                "1098edadc345ec948d37e1541ed867eb",
                "fb60e0a42a0f7f0929f5a5ae401a3518",
            },
        ),
        (
            "https://lensdump.com/a/Vb411",  # Album
            {
                "9ceac1e26c4799b0a6b7d5453a73f53b",
                "54391b5210286bd01224f1f513159e82",
                "907f92b1c295d5f84f4f64aacc960079",
                "14d911ebc49fb82e5657c8ac827a2b32",
                "a66d093b4fe19a1cb4b5e10bc34d17bb",
            },
        ),
        (
            "https://nsfw.pics/image/OdfV",  # Single image
            {"9ceac1e26c4799b0a6b7d5453a73f53b"},
        ),
        (
            "https://lensdump.com/i/CDIUci",  # Single image
            {"9ceac1e26c4799b0a6b7d5453a73f53b"},
        ),
    ),
)
def test_download_resources(test_url: str, expected_hashes: set[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Chevereto(mock_download)
    results = downloader.find_resources()
    assert all(isinstance(res, Resource) for res in results)
    [res.download() for res in results]
    hashes = {res.hash.hexdigest() for res in results}
    assert hashes == set(expected_hashes)
