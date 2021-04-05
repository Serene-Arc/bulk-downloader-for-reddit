#!/usr/bin/env python3
# coding=utf-8

import hashlib
import logging
import re
import time
from typing import Optional

import _hashlib
import requests
from praw.models import Submission

from bulkredditdownloader.exceptions import BulkDownloaderException

logger = logging.getLogger(__name__)


class Resource:
    def __init__(self, source_submission: Submission, url: str, extension: str = None):
        self.source_submission = source_submission
        self.content: Optional[bytes] = None
        self.url = url
        self.hash: Optional[_hashlib.HASH] = None
        self.extension = extension
        if not self.extension:
            self.extension = self._determine_extension()

    @staticmethod
    def retry_download(url: str, wait_time: int) -> Optional[bytes]:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            elif response.status_code in (301, 401, 403, 404):
                raise BulkDownloaderException(f'Unrecoverable error requesting resource: HTTP Code {response.status_code}')
            else:
                raise requests.exceptions.ConnectionError(f'Response code {response.status_code}')
        except requests.exceptions.ConnectionError as e:
            logger.log(9, f'Error occured downloading resource, waiting {wait_time} seconds: {e}')
            time.sleep(wait_time)
            if wait_time < 300:
                return Resource.retry_download(url, wait_time + 60)
            else:
                logger.error(f'Max wait time exceeded for resource at url {url}')
                raise

    def download(self):
        if not self.content:
            try:
                content = self.retry_download(self.url, 0)
            except requests.exceptions.ConnectionError as e:
                raise BulkDownloaderException(f'Could not download resource: {e}')
            except BulkDownloaderException:
                raise
            if content:
                self.content = content
        if not self.hash and self.content:
            self.create_hash()

    def create_hash(self):
        self.hash = hashlib.md5(self.content)

    def _determine_extension(self) -> str:
        extension_pattern = re.compile(r'.*(\..{3,5})(?:\?.*)?$')
        match = re.search(extension_pattern, self.url)
        if match:
            return match.group(1)
