from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.flickr import Flickr


@pytest.mark.online
def test_key_cache():
    key1 = Flickr._get_api_key()
    key2 = Flickr._get_api_key()
    assert key1 == key2


@pytest.mark.parametrize(
    ("test_url", "expected_user", "expected_id"),
    (
        ("https://www.flickr.com/photos/137434519@N08/33635695603", "137434519@N08", "33635695603"),  # Single photo
        (
            "https://www.flickr.com/photos/63215229@N04/albums/72157644975251416",  # Album
            "63215229@N04",
            "72157644975251416",
        ),
    ),
)
def test_get_ids(test_url: str, expected_user: str, expected_id: str):
    user, f_id = Flickr._get_ids(test_url)
    assert user == expected_user
    assert f_id == expected_id


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_url"),
    (
        (
            "https://www.flickr.com/gp/137434519@N08/83Q029",  # /gp/ link
            "https://www.flickr.com/photos/137434519@N08/33635695603/",
        ),
        ("https://flic.kr/p/2k5E4mv", "https://www.flickr.com/photos/129756120@N03/50592162657/"),  # flic.kr link
    ),
)
def test_expand_url(test_url: str, expected_url: str):
    link = Flickr._expand_link(test_url)
    assert link == expected_url


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_id", "expected_user"),
    (("buta_suneo", "63215229@N04"),),  # username to user ID
)
def test_get_user_id(test_id: str, expected_user: str):
    api_key = Flickr._get_api_key()
    api_string = f"https://www.flickr.com/services/rest/?api_key={api_key}&format=json&nojsoncallback=1&"
    user = Flickr._get_user_id(test_id, api_string)
    assert user == expected_user


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        ("https://www.flickr.com/gp/137434519@N08/83Q029", {"b3f4e6fca1cc0ffca55368e4f94f9b5f"}),  # Single photo
        ("https://flic.kr/p/2k5E4mv", {"75ae4f5e70b9b7525041b1dcc852d144"}),  # Single photo
        (
            "http://www.flickr.com/photos/thekog/6886709962/",  # Single photo
            {"a4a64e606368f7b5a1995c84e15463e9"},
        ),
        (
            "https://www.flickr.com/photos/ochre_jelly/albums/72157708743730852",  # Album
            {
                "3c442ffdadff7b02cb7a133865339a26",
                "8023fc0e76f891d585871ddd64edac23",
                "9bbedad97b59ec51cb967da507351912",
                "a86fcd3458620eec4cb3606882d11e9a",
                "addb62d788c542383d1ad47914bbefb3",
            },
        ),
        ("https://www.flickr.com/photos/eerokiuru/52902303276", {"adfd8175f398f87744285da2591c8215"}),  # Single video
    ),
)
def test_download_resource(test_url: str, expected_hashes: set[str]):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Flickr(mock_submission)
    results = test_site.find_resources()
    assert all(isinstance(res, Resource) for res in results)
    [res.download() for res in results]
    hashes = {res.hash.hexdigest() for res in results}
    assert hashes == set(expected_hashes)
