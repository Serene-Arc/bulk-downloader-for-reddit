#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest


@pytest.fixture(scope='session')
def reddit_instance():
    rd = praw.Reddit(client_id='U-6gk4ZCh3IeNQ', client_secret='7CZHY6AmKweZME5s50SfDGylaPg', user_agent='test')
    return rd
