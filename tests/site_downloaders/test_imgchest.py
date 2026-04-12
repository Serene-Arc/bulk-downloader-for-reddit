from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.imgchest import Imgchest


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://www.imgchest.com/p/ro24aogylj5",  # Basic image album
            {
                "https://cdn.imgchest.com/files/jd7ogcgl5y9.jpg",
                "https://cdn.imgchest.com/files/rj7kzcdv27m.jpg",
                "https://cdn.imgchest.com/files/vmy2pc2pr7j.jpg",
                "https://cdn.imgchest.com/files/xl7lxce967o.jpg",
            },
        ),
        (
            "https://www.imgchest.com/p/o24ap5wd4lj",  # Image and video album
            {
                "https://cdn.imgchest.com/files/k46ac86kq7z.jpeg",
                "https://cdn.imgchest.com/files/pyvdczlvayk.jpeg",
                "https://cdn.imgchest.com/files/6yxkcvlrn7w.jpeg",
                "https://cdn.imgchest.com/files/b49zce5wkyw.jpeg",
                "https://cdn.imgchest.com/files/l4necb3kw4m.jpeg",
                "https://cdn.imgchest.com/files/p7bwc3rx37n.mp4",
                "https://cdn.imgchest.com/files/w7pjcbe587p.mp4",
                "https://cdn.imgchest.com/files/d7ogcr95jy9.mp4",
                "https://cdn.imgchest.com/files/j7kzc9r557m.mp4",
                "https://cdn.imgchest.com/files/my2pc3wzl7j.mp4",
            },
        ),
    ),
)
def test_get_links(test_url: str, expected: set[str]):
    results = Imgchest._get_links(test_url)
    assert results == expected


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        (
            "https://www.imgchest.com/p/ro24aogylj5",  # Basic image album
            {
                "91f1a5919b32af6cbf5c24528e83871c",
                "c4969ac347fdcefbb6b2ec01c0be02ae",
                "a9db23217974d8b78c84b463224f130a",
                "6a0d0e28f02c2cdccff80f9973efbad3",
            },
        ),
        (
            "https://www.imgchest.com/p/o24ap5wd4lj",  # Image and video album
            {
                "a4ea3f676c8a1cbca8e2faf70a031e1e",
                "59db5f35f5969d638c4036a3a249b1e1",
                "73ee75fe341022cd643431a4fb78be3d",
                "6fe6f1239dd39f948b3abb583c310c7d",
                "8e9b652c62b906ba54607c7fd8ce6d63",
                "108b167b04830ce0a59c27415bb5ef86",
                "05a063fe87fb010ca782c268d0bf90c5",
                "5ef705919760684d54e082430f32551a",
                "7ff437036cac57e04aaabcfd604ad2c8",
                "d2e3eb303f3a605b2a8587f914b78c34",
            },
        ),
    ),
)
def test_download_resources(test_url: str, expected_hashes: set[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Imgchest(mock_download)
    results = downloader.find_resources()
    assert all(isinstance(res, Resource) for res in results)
    [res.download() for res in results]
    hashes = {res.hash.hexdigest() for res in results}
    assert hashes == set(expected_hashes)
