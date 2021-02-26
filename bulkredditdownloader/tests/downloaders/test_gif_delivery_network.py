#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import Mock

import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.gif_delivery_network import GifDeliveryNetwork


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected'), (
    ('https://www.gifdeliverynetwork.com/handyunsightlydesertpupfish',
     'https://thumbs2.redgifs.com/HandyUnsightlyDesertpupfish.mp4'),
    ('https://www.gifdeliverynetwork.com/lamelikelyhamadryad',
     'https://thumbs2.redgifs.com/LameLikelyHamadryad.mp4')
))
def test_get_link(test_url: str, expected: str):
    result = GifDeliveryNetwork._get_link(test_url)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(('test_url', 'expected_hash'), (
    ('https://www.gifdeliverynetwork.com/handyunsightlydesertpupfish', 'd941460dcf4e0d09dd33abaa32e2d270'),
    ('https://www.gifdeliverynetwork.com/lamelikelyhamadryad', '4806fe15f4991bb73581338793488daf'),
))
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock
    mock_submission.url = test_url
    test_site = GifDeliveryNetwork(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
