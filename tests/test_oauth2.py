#!/usr/bin/env python3

import configparser
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import BulkDownloaderException
from bdfr.oauth2 import OAuth2Authenticator


@pytest.fixture()
def example_config() -> configparser.ConfigParser:
    out = configparser.ConfigParser()
    config_dict = {"DEFAULT": {"user_token": "example"}}
    out.read_dict(config_dict)
    return out


@pytest.mark.online
@pytest.mark.parametrize(
    "test_scopes",
    (
        {
            "history",
        },
        {"history", "creddits"},
        {"account", "flair"},
        {
            "*",
        },
    ),
)
def test_check_scopes(test_scopes: set[str]):
    OAuth2Authenticator._check_scopes(test_scopes, "fetch-scopes test")


@pytest.mark.parametrize(
    ("test_scopes", "expected"),
    (
        (
            "history",
            {
                "history",
            },
        ),
        ("history creddits", {"history", "creddits"}),
        ("history, creddits, account", {"history", "creddits", "account"}),
        ("history,creddits,account,flair", {"history", "creddits", "account", "flair"}),
    ),
)
def test_split_scopes(test_scopes: str, expected: set[str]):
    result = OAuth2Authenticator.split_scopes(test_scopes)
    assert result == expected


@pytest.mark.online
@pytest.mark.parametrize(
    "test_scopes",
    (
        {
            "random",
        },
        {"scope", "another_scope"},
    ),
)
def test_check_scopes_bad(test_scopes: set[str]):
    with pytest.raises(BulkDownloaderException):
        OAuth2Authenticator._check_scopes(test_scopes, "fetch-scopes test")
