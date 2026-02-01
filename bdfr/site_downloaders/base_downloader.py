#!/usr/bin/env python3

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
    def __init__(self, post: Submission, typical_extension: Optional[str] = None) -> None:
        self.post = post
        self.typical_extension = typical_extension

    @abstractmethod
    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        """Return list of all un-downloaded Resources from submission"""
        raise NotImplementedError

    @staticmethod
    def retrieve_url(
        url: str,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        try:
            res = requests.get(url, cookies=cookies, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Failed to get page {url}")
        except TimeoutError as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Timeout reached attempting to get page {url}")
        if res.status_code != 200:
            raise ResourceNotFound(f"Server responded with {res.status_code} at {url}")
        return res

    @staticmethod
    def post_url(
        url: str,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> requests.Response:
        try:
            res = requests.post(url, cookies=cookies, headers=headers, json=payload, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Failed to post to {url}")
        except TimeoutError as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Timeout reached attempting to post to page {url}")
        if res.status_code != 200:
            raise ResourceNotFound(f"Server responded with {res.status_code} to {url}")
        return res

    @staticmethod
    def head_url(url: str, cookies: Optional[dict] = None, headers: Optional[dict] = None) -> requests.Response:
        try:
            res = requests.head(url, cookies=cookies, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Failed to check head at {url}")
        except TimeoutError as e:
            logger.exception(e)
            raise SiteDownloaderError(f"Timeout reached attempting to check head at {url}")
        return res
