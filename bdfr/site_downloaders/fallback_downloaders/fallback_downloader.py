#!/usr/bin/env python3
# coding=utf-8

from abc import ABC, abstractmethod

from bdfr.site_downloaders.base_downloader import BaseDownloader


class BaseFallbackDownloader(BaseDownloader, ABC):

    @staticmethod
    @abstractmethod
    def can_handle_link(url: str) -> bool:
        """Returns whether the fallback downloader can download this link"""
        raise NotImplementedError
