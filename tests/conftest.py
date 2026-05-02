#!/usr/bin/env python3

import configparser
import socket
from pathlib import Path

import praw
import pytest


@pytest.fixture(scope="session")
def reddit_instance():
    rd = praw.Reddit(
        client_id="U-6gk4ZCh3IeNQ",
        client_secret="7CZHY6AmKweZME5s50SfDGylaPg",
        user_agent="test",
    )
    return rd


@pytest.fixture(scope="session")
def authenticated_reddit_instance():
    test_config_path = Path("./tests/test_config.cfg")
    if not test_config_path.exists():
        pytest.skip("Refresh token must be provided to authenticate with OAuth2")
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(test_config_path)
    if not cfg_parser.has_option("DEFAULT", "user_token"):
        pytest.skip("Refresh token must be provided to authenticate with OAuth2")
    reddit_instance = praw.Reddit(
        client_id=cfg_parser.get("DEFAULT", "client_id"),
        client_secret=cfg_parser.get("DEFAULT", "client_secret"),
        user_agent=socket.gethostname(),
        refresh_token=cfg_parser.get("DEFAULT", "user_token"),
    )
    return reddit_instance
