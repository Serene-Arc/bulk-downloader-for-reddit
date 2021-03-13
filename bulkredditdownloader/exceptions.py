#!/usr/bin/env

class BulkDownloaderException(Exception):
    pass


class RedditUserError(BulkDownloaderException):
    pass


class RedditAuthenticationError(RedditUserError):
    pass


class ArchiverError(BulkDownloaderException):
    pass


class SiteDownloaderError(BulkDownloaderException):
    pass


class NotADownloadableLinkError(SiteDownloaderError):
    pass


class ResourceNotFound(SiteDownloaderError):
    pass
