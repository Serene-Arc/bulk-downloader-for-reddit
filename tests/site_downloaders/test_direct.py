#!/usr/bin/env python3

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.direct import Direct


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (
        ("https://i.redd.it/q6ebualjxzea1.jpg", "6ec154859c777cb401132bb991cb3635"),
        ("https://filesamples.com/samples/audio/mp3/sample3.mp3", "d30a2308f188cbb11d74cf20c357891c"),
    ),
)
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Direct(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
