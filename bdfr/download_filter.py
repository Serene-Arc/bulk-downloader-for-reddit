#!/usr/bin/env python3
# coding=utf-8

import logging
import re

from bdfr.resource import Resource

logger = logging.getLogger(__name__)


class DownloadFilter:
    def __init__(self, excluded_extensions: list[str] = None, excluded_domains: list[str] = None):
        self.excluded_extensions = excluded_extensions
        self.excluded_domains = excluded_domains

    def check_url(self, url: str) -> bool:
        """Return whether a URL is allowed or not"""
        if not self._check_extension(url):
            return False
        elif not self._check_domain(url):
            return False
        else:
            return True

    def check_resource(self, res: Resource) -> bool:
        if not self._check_extension(res.extension):
            return False
        elif not self._check_domain(res.url):
            return False
        return True

    def _check_extension(self, resource_extension: str) -> bool:
        if not self.excluded_extensions:
            return True
        combined_extensions = '|'.join(self.excluded_extensions)
        pattern = re.compile(r'.*({})$'.format(combined_extensions))
        if re.match(pattern, resource_extension):
            logger.log(9, f'Url "{resource_extension}" matched with "{str(pattern)}"')
            return False
        else:
            return True

    def _check_domain(self, url: str) -> bool:
        if not self.excluded_domains:
            return True
        combined_domains = '|'.join(self.excluded_domains)
        pattern = re.compile(r'https?://.*({}).*'.format(combined_domains))
        if re.match(pattern, url):
            logger.log(9, f'Url "{url}" matched with "{str(pattern)}"')
            return False
        else:
            return True
