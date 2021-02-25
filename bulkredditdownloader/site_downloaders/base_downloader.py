#!/usr/bin/env python3
# coding=utf-8

import logging
from abc import ABC, abstractmethod
from typing import Optional

from praw.models import Submission

from bulkredditdownloader.authenticator import Authenticator
from bulkredditdownloader.resource import Resource

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    def __init__(self, post: Submission, typical_extension: Optional[str] = None):
        self.post = post
        self.typical_extension = typical_extension

    @abstractmethod
    def find_resources(self, authenticator: Optional[Authenticator] = None) -> list[Resource]:
        """Return list of all un-downloaded Resources from submission"""
        raise NotImplementedError
