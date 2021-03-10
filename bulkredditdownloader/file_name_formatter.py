#!/usr/bin/env python3
# coding=utf-8

import re
from pathlib import Path

import praw.models

from bulkredditdownloader.exceptions import BulkDownloaderException
from bulkredditdownloader.resource import Resource


class FileNameFormatter:
    key_terms = ('title', 'subreddit', 'redditor', 'postid', 'upvotes', 'flair', 'date')

    def __init__(self, file_format_string: str, directory_format_string: str):
        if not self.validate_string(file_format_string):
            raise BulkDownloaderException(f'"{file_format_string}" is not a valid format string')
        self.file_format_string = file_format_string
        self.directory_format_string = directory_format_string

    @staticmethod
    def _format_name(submission: praw.models.Submission, format_string: str) -> str:
        submission_attributes = {
            'title': submission.title,
            'subreddit': submission.subreddit.display_name,
            'redditor': submission.author.name,
            'postid': submission.id,
            'upvotes': submission.score,
            'flair': submission.link_flair_text,
            'date': submission.created_utc
        }
        result = format_string
        for key in submission_attributes.keys():
            if re.search(r'(?i).*{{{}}}.*'.format(key), result):
                result = re.sub(r'(?i){{{}}}'.format(key), str(submission_attributes.get(key, 'unknown')), result)

        result = result.replace('/', '')
        return result

    def format_path(self, resource: Resource, destination_directory: Path) -> Path:
        subfolder = destination_directory / self._format_name(resource.source_submission, self.directory_format_string)
        file_path = subfolder / (str(self._format_name(resource.source_submission,
                                                       self.file_format_string)) + resource.extension)
        return file_path

    @staticmethod
    def validate_string(test_string: str) -> bool:
        if not test_string:
            return False
        return any([f'{{{key}}}' in test_string.lower() for key in FileNameFormatter.key_terms])
