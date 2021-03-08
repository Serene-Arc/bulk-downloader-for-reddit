#!/usr/bin/env python3
# coding=utf-8

import configparser
from unittest.mock import MagicMock

import praw
import pytest

from bulkredditdownloader.exceptions import BulkDownloaderException
from bulkredditdownloader.oauth2 import OAuth2Authenticator, OAuth2TokenManager


@pytest.fixture()
def example_config() -> configparser.ConfigParser:
    out = configparser.ConfigParser()
    config_dict = {'DEFAULT': {'user_token': 'example'}}
    out.read_dict(config_dict)
    return out


@pytest.mark.online
@pytest.mark.parametrize('test_scopes', (
    ('history',),
    ('history', 'creddits'),
    ('account', 'flair'),
    ('*',),
))
def test_check_scopes(test_scopes: list[str]):
    OAuth2Authenticator._check_scopes(test_scopes)


@pytest.mark.online
@pytest.mark.parametrize('test_scopes', (
    ('random',),
    ('scope', 'another_scope'),
))
def test_check_scopes_bad(test_scopes: list[str]):
    with pytest.raises(BulkDownloaderException):
        OAuth2Authenticator._check_scopes(test_scopes)


def test_token_manager_read(example_config: configparser.ConfigParser):
    mock_authoriser = MagicMock()
    mock_authoriser.refresh_token = None
    test_manager = OAuth2TokenManager(example_config)
    test_manager.pre_refresh_callback(mock_authoriser)
    assert mock_authoriser.refresh_token == example_config.get('DEFAULT', 'user_token')


def test_token_manager_write(example_config: configparser.ConfigParser):
    mock_authoriser = MagicMock()
    mock_authoriser.refresh_token = 'changed_token'
    test_manager = OAuth2TokenManager(example_config)
    test_manager.post_refresh_callback(mock_authoriser)
    assert example_config.get('DEFAULT', 'user_token') == 'changed_token'
