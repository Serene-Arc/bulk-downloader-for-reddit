#!/usr/bin/env

class BulkDownloaderException(Exception):
    pass


class NotADownloadableLinkError(BulkDownloaderException):
    pass


class RedditAuthenticationError(BulkDownloaderException):
    pass


class InvalidJSONFile(BulkDownloaderException):
    pass


class FailedToDownload(BulkDownloaderException):
    pass


class ImageNotFound(BulkDownloaderException):
    pass


class ExtensionError(BulkDownloaderException):
    pass
