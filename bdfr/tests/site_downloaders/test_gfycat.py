#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.gfycat import Gfycat


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_url'), (
    ('https://gfycat.com/definitivecaninecrayfish', 'https://giant.gfycat.com/DefinitiveCanineCrayfish.mp4'),
    ('https://gfycat.com/dazzlingsilkyiguana', 'https://giant.gfycat.com/DazzlingSilkyIguana.mp4'),
    ('https://gfycat.com/webbedimpurebutterfly', 'https://thumbs2.redgifs.com/WebbedImpureButterfly.mp4'),
))
def test_get_link(test_url: str, expected_url: str):
    result = Gfycat._get_link(test_url)
    assert result == expected_url


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://gfycat.com/definitivecaninecrayfish', '48f9bd4dbec1556d7838885612b13b39'),
    ('https://gfycat.com/dazzlingsilkyiguana', '808941b48fc1e28713d36dd7ed9dc648'),
))
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Gfycat(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].hash.hexdigest() == expected_hash
