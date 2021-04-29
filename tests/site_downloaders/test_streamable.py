#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.streamable import Streamable


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://streamable.com/dt46y', '1e7f4928e55de6e3ca23d85cc9246bbb'),
    ('https://streamable.com/t8sem', '49b2d1220c485455548f1edbc05d4ecf')
))
def test_find_resources(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = Streamable(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].hash.hexdigest() == expected_hash
