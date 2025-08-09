#!/usr/bin/env python3

import praw
import pytest

from bdfr.exceptions import SiteDownloaderError
from bdfr.site_downloaders.gallery import Gallery


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_ids", "expected"),
    (
        (
            [
                {"media_id": "18nzv9ch0hn61"},
                {"media_id": "jqkizcch0hn61"},
                {"media_id": "k0fnqzbh0hn61"},
                {"media_id": "m3gamzbh0hn61"},
            ],
            {
                "https://i.redd.it/18nzv9ch0hn61.jpg",
                "https://i.redd.it/jqkizcch0hn61.jpg",
                "https://i.redd.it/k0fnqzbh0hn61.jpg",
                "https://i.redd.it/m3gamzbh0hn61.jpg",
            },
        ),
        (
            [
                {"media_id": "04vxj25uqih61"},
                {"media_id": "0fnx83kpqih61"},
                {"media_id": "7zkmr1wqqih61"},
                {"media_id": "u37k5gxrqih61"},
            ],
            {
                "https://i.redd.it/04vxj25uqih61.png",
                "https://i.redd.it/0fnx83kpqih61.png",
                "https://i.redd.it/7zkmr1wqqih61.png",
                "https://i.redd.it/u37k5gxrqih61.png",
            },
        ),
    ),
)
def test_gallery_get_links(test_ids: list[dict], expected: set[str]):
    results = Gallery._get_links(test_ids)
    assert set(results) == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("test_submission_id", "expected_hashes"),
    (
        (
            "m6lvrh",
            {
                "5c42b8341dd56eebef792e86f3981c6a",
                "8f38d76da46f4057bf2773a778e725ca",
                "f5776f8f90491c8b770b8e0a6bfa49b3",
                "fa1a43c94da30026ad19a9813a0ed2c2",
            },
        ),
        (
            "w22m5l",
            {
                "26aa07eed6dd0bd0ec871a9dcdd572ef",
                "7e8d2dc005b1270947a0cef4cd64238f",
            },
        ),
        (
            "obkflw",
            {
                "65163f685fb28c5b776e0e77122718be",
                "2a337eb5b13c34d3ca3f51b5db7c13e9",
            },
        ),
        (
            "rb3ub6",
            {  # patreon post
                "748a976c6cedf7ea85b6f90e7cb685c7",
                "839796d7745e88ced6355504e1f74508",
                "bcdb740367d0f19f97a77e614b48a42d",
                "0f230b8c4e5d103d35a773fab9814ec3",
                "e5192d6cb4f84c4f4a658355310bf0f9",
                "91cbe172cd8ccbcf049fcea4204eb979",
            },
        ),
    ),
)
def test_gallery_download(test_submission_id: str, expected_hashes: set[str], reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    gallery = Gallery(test_submission)
    results = gallery.find_resources()
    [res.download() for res in results]
    hashes = [res.hash.hexdigest() for res in results]
    assert set(hashes) == expected_hashes


@pytest.mark.parametrize(
    "test_id",
    (
        "n0pyzp",
        "nxyahw",
    ),
)
def test_gallery_download_raises_right_error(test_id: str, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_id)
    gallery = Gallery(test_submission)
    with pytest.raises(SiteDownloaderError):
        gallery.find_resources()
