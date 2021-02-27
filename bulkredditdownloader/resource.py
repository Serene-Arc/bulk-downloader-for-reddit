#!/usr/bin/env python3
# coding=utf-8

import hashlib
import re
import time
from typing import Optional

import _hashlib
import requests
from praw.models import Submission

from bulkredditdownloader.errors import BulkDownloaderException


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
            else:
                raise requests.exceptions.ConnectionError
        except requests.exceptions.ConnectionError:
            time.sleep(wait_time)
            if wait_time < 300:
                return Resource.retry_download(url, wait_time + 60)
            else:
                return None

    def download(self):
        if not self.content:
            content = self.retry_download(self.url, 0)
            if content:
                self.content = content
                self.create_hash()
            else:
                raise BulkDownloaderException('Could not download resource')

    def create_hash(self):
        self.hash = hashlib.md5(self.content)

    def _determine_extension(self) -> str:
        extension_pattern = r'.*(\..{3,5})$'
        match = re.search(extension_pattern, self.url)
        if match:
            return match.group(1)
