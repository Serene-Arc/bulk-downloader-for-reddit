#!/usr/bin/env python3

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.delay_for_reddit import DelayForReddit


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (
        ("https://www.delayforreddit.com/dfr/calvin6123/MjU1Njc5NQ==", "3300f28c2f9358d05667985c9c04210d"),
        ("https://www.delayforreddit.com/dfr/RoXs_26/NDAwMzAyOQ==", "09b7b01719dff45ab197bdc08b90f78a"),
    ),
)
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = DelayForReddit(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
