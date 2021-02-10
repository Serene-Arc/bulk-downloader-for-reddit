#!/usr/bin/env python3
# coding=utf-8

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from praw.models import Submission

from bulkredditdownloader.errors import FailedToDownload
from bulkredditdownloader.resource import Resource

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    def __init__(self, directory: Path, post: Submission):
        self.directory = directory
        self.post = post
        self.hashes = []

    @abstractmethod
    def download(self) -> list[Resource]:
        raise NotImplementedError

    def _download_resource(self, resource_url: str):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 "
            "Safari/537.36 OPR/54.0.2952.64",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        # Loop to attempt download 3 times
        for i in range(3):
            try:
                download_content = requests.get(resource_url, headers=headers).content
            except ConnectionResetError:
                raise FailedToDownload
            return Resource(self.post, resource_url, download_content)

        raise FailedToDownload
