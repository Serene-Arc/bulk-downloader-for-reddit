#!/usr/bin/env

class BulkDownloaderException(Exception):
    pass


class RedditAuthenticationError(BulkDownloaderException):
    pass


class SiteDownloaderError(BulkDownloaderException):
    pass


class NotADownloadableLinkError(SiteDownloaderError):
    pass


class ResourceNotFound(SiteDownloaderError):
    pass
