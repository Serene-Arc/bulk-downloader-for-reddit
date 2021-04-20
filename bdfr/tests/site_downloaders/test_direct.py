#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.direct import Direct


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://giant.gfycat.com/DefinitiveCanineCrayfish.mp4', '48f9bd4dbec1556d7838885612b13b39'),
    ('https://giant.gfycat.com/DazzlingSilkyIguana.mp4', '808941b48fc1e28713d36dd7ed9dc648'),
))
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Direct(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download(120)
    assert resources[0].hash.hexdigest() == expected_hash
