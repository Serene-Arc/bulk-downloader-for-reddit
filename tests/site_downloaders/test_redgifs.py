#!/usr/bin/env python3

import re
from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.redgifs import Redgifs


@pytest.mark.online
def test_auth_cache():
    auth1 = Redgifs._get_auth_token()
    auth2 = Redgifs._get_auth_token()
    assert auth1 == auth2


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("https://redgifs.com/watch/frighteningvictorioussalamander", "frighteningvictorioussalamander"),
        ("https://www.redgifs.com/watch/genuineprivateguillemot/", "genuineprivateguillemot"),
        ("https://www.redgifs.com/watch/marriedcrushingcob?rel=u%3Akokiri.girl%3Bo%3Arecent", "marriedcrushingcob"),
        ("https://thumbs4.redgifs.com/DismalIgnorantDrongo.mp4", "dismalignorantdrongo"),
        ("https://thumbs4.redgifs.com/DismalIgnorantDrongo-mobile.mp4", "dismalignorantdrongo"),
        ("https://v3.redgifs.com/watch/newilliteratemeerkat#rel=user%3Atastynova", "newilliteratemeerkat"),
        ("https://thumbs46.redgifs.com/BabyishCharmingAidi-medium.jpg", "babyishcharmingaidi"),
    ),
)
def test_get_id(test_url: str, expected: str):
    result = Redgifs._get_id(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("https://redgifs.com/watch/frighteningvictorioussalamander", {"FrighteningVictoriousSalamander.mp4"}),
        ("https://redgifs.com/watch/springgreendecisivetaruca", {"SpringgreenDecisiveTaruca.mp4"}),
        ("https://www.redgifs.com/watch/palegoldenrodrawhalibut", {"PalegoldenrodRawHalibut.mp4"}),
        ("https://redgifs.com/watch/hollowintentsnowyowl", {"HollowIntentSnowyowl-large.jpg"}),
        ("https://www.redgifs.com/watch/genuineprivateguillemot/", {"GenuinePrivateGuillemot.mp4"}),
    ),
)
def test_get_link(test_url: str, expected: set[str]):
    result = Redgifs._get_link(test_url)
    result = list(result)
    patterns = [r"https://thumbs\d\.redgifs\.com/" + e + r".*" for e in expected]
    assert all([re.match(p, r) for p in patterns] for r in result)


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        ("https://redgifs.com/watch/frighteningvictorioussalamander", {"4007c35d9e1f4b67091b5f12cffda00a"}),
        ("https://redgifs.com/watch/springgreendecisivetaruca", {"8dac487ac49a1f18cc1b4dabe23f0869"}),
        ("https://redgifs.com/watch/leafysaltydungbeetle", {"076792c660b9c024c0471ef4759af8bd"}),
        ("https://www.redgifs.com/watch/palegoldenrodrawhalibut", {"46d5aa77fe80c6407de1ecc92801c10e"}),
        ("https://redgifs.com/watch/hollowintentsnowyowl", {"5ee51fa15e0a58e98f11dea6a6cca771"}),
        ("https://thumbs46.redgifs.com/BabyishCharmingAidi-medium.jpg", {"bf14b9f3d5b630cb5fd271661226f1af"}),
    ),
)
def test_download_resource(test_url: str, expected_hashes: set[str]):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Redgifs(mock_submission)
    results = test_site.find_resources()
    assert all([isinstance(res, Resource) for res in results])
    [res.download() for res in results]
    hashes = set([res.hash.hexdigest() for res in results])
    assert hashes == set(expected_hashes)


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_link", "expected_hash"),
    (
        (
            "https://redgifs.com/watch/flippantmemorablebaiji",
            {"FlippantMemorableBaiji-mobile.mp4"},
            {"41a5fb4865367ede9f65fc78736f497a"},
        ),
        (
            "https://redgifs.com/watch/conventionalplainxenopterygii",
            {"conventionalplainxenopterygii-mobile.mp4"},
            {"2e1786b3337da85b80b050e2c289daa4"},
        ),
    ),
)
def test_hd_soft_fail(test_url: str, expected_link: set[str], expected_hash: set[str]):
    link = Redgifs._get_link(test_url)
    link = list(link)
    patterns = [r"https://thumbs\d\.redgifs\.com/" + e + r".*" for e in expected_link]
    assert all([re.match(p, r) for p in patterns] for r in link)
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Redgifs(mock_submission)
    results = test_site.find_resources()
    assert all([isinstance(res, Resource) for res in results])
    [res.download() for res in results]
    hashes = set([res.hash.hexdigest() for res in results])
    assert hashes == set(expected_hash)
