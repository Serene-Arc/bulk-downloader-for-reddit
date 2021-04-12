#!/usr/bin/env python3
# coding=utf-8

import configparser
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import BulkDownloaderException
from bdfr.oauth2 import OAuth2Authenticator, OAuth2TokenManager


@pytest.fixture()
def example_config() -> configparser.ConfigParser:
    out = configparser.ConfigParser()
    config_dict = {'DEFAULT': {'user_token': 'example'}}
    out.read_dict(config_dict)
    return out


@pytest.mark.online
@pytest.mark.parametrize('test_scopes', (
    {'history', },
    {'history', 'creddits'},
    {'account', 'flair'},
    {'*', },
))
def test_check_scopes(test_scopes: set[str]):
    OAuth2Authenticator._check_scopes(test_scopes)


@pytest.mark.parametrize(('test_scopes', 'expected'), (
    ('history', {'history', }),
    ('history creddits', {'history', 'creddits'}),
    ('history, creddits, account', {'history', 'creddits', 'account'}),
    ('history,creddits,account,flair', {'history', 'creddits', 'account', 'flair'}),
))
def test_split_scopes(test_scopes: str, expected: set[str]):
    result = OAuth2Authenticator.split_scopes(test_scopes)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize('test_scopes', (
    {'random', },
    {'scope', 'another_scope'},
))
def test_check_scopes_bad(test_scopes: set[str]):
    with pytest.raises(BulkDownloaderException):
        OAuth2Authenticator._check_scopes(test_scopes)


def test_token_manager_read(example_config: configparser.ConfigParser):
    mock_authoriser = MagicMock()
    mock_authoriser.refresh_token = None
    test_manager = OAuth2TokenManager(example_config, MagicMock())
    test_manager.pre_refresh_callback(mock_authoriser)
    assert mock_authoriser.refresh_token == example_config.get('DEFAULT', 'user_token')


def test_token_manager_write(example_config: configparser.ConfigParser, tmp_path: Path):
    test_path = tmp_path / 'test.cfg'
    mock_authoriser = MagicMock()
    mock_authoriser.refresh_token = 'changed_token'
    test_manager = OAuth2TokenManager(example_config, test_path)
    test_manager.post_refresh_callback(mock_authoriser)
    assert example_config.get('DEFAULT', 'user_token') == 'changed_token'
    with open(test_path, 'r') as file:
        file_contents = file.read()
    assert 'user_token = changed_token' in file_contents
