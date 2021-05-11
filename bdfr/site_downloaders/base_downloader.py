#!/usr/bin/env python3
# coding=utf-8

import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests
from praw.models import Submission

from bdfr.exceptions import ResourceNotFound, SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    def __init__(self, post: Submission, typical_extension: Optional[str] = None):
        self.post = post
        self.typical_extension = typical_extension

    @abstractmethod
    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        """Return list of all un-downloaded Resources from submission"""
        raise NotImplementedError

    @staticmethod
    def retrieve_url(url: str, cookies: dict = None, headers: dict = None) -> requests.Response:
        try:
            res = requests.get(url, cookies=cookies, headers=headers)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            raise SiteDownloaderError(f'Failed to get page {url}')
        if res.status_code != 200:
            raise ResourceNotFound(f'Server responded with {res.status_code} to {url}')
        return res
