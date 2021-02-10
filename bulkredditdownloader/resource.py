#!/usr/bin/env python3
# coding=utf-8

import hashlib
import re

from praw.models import Submission


class Resource:
    def __init__(self, source_submission: Submission, url: str, content: bytes):
        self.source_submission = source_submission
        self.content = content
        self.url = url
        self.hash = hashlib.md5(content)
        self.extension = self._get_extension(url)

    @staticmethod
    def _get_extension(url: str) -> str:
        pattern = re.compile(r'(\.(jpg|jpeg|png|mp4|webm|gif))')
        if results := re.search(pattern, url):
            if len(results.groups()) > 1:
                return results[0]
        if "v.redd.it" not in url:
            return '.jpg'
        else:
            return '.mp4'
