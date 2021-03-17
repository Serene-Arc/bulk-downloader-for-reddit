#!/usr/bin/env python3
# coding=utf-8

import logging
import re
from pathlib import Path
from typing import Optional

import praw.models

from bulkredditdownloader.exceptions import BulkDownloaderException
from bulkredditdownloader.resource import Resource

logger = logging.getLogger(__name__)


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
            'redditor': submission.author.name if submission.author else 'DELETED',
            'postid': submission.id,
            'upvotes': submission.score,
            'flair': submission.link_flair_text,
            'date': submission.created_utc
        }
        result = format_string
        for key in submission_attributes.keys():
            if re.search(r'(?i).*{{{}}}.*'.format(key), result):
                result = re.sub(r'(?i){{{}}}'.format(key), str(submission_attributes.get(key, 'unknown')), result)
                logger.log(9, f'Found key string {key} in name')

        result = result.replace('/', '')
        return result

    def format_path(self, resource: Resource, destination_directory: Path, index: Optional[int] = None) -> Path:
        subfolder = destination_directory / self._format_name(resource.source_submission, self.directory_format_string)
        index = f'_{str(index)}' if index else ''
        if not resource.extension:
            raise BulkDownloaderException(f'Resource from {resource.url} has no extension')
        ending = index + resource.extension
        file_name = str(self._format_name(resource.source_submission, self.file_format_string))
        file_name = self._limit_file_name_length(file_name, ending)
        try:
            file_path = Path(subfolder, file_name)
        except TypeError:
            raise BulkDownloaderException(f'Could not determine path name: {subfolder}, {index}, {resource.extension}')
        return file_path

    @staticmethod
    def _limit_file_name_length(filename: str, ending: str) -> str:
        max_length_chars = 255 - len(ending)
        max_length_bytes = 255 - len(ending.encode('utf-8'))
        while len(filename) > max_length_chars or len(filename.encode('utf-8')) > max_length_bytes:
            filename = filename[:-1]
        return filename + ending

    def format_resource_paths(self, resources: list[Resource],
                              destination_directory: Path) -> list[tuple[Path, Resource]]:
        out = []
        if len(resources) == 1:
            out.append((self.format_path(resources[0], destination_directory, None), resources[0]))
        else:
            for i, res in enumerate(resources, start=1):
                logger.log(9, f'Formatting filename with index {i}')
                out.append((self.format_path(res, destination_directory, i), res))
        return out

    @ staticmethod
    def validate_string(test_string: str) -> bool:
        if not test_string:
            return False
        return any([f'{{{key}}}' in test_string.lower() for key in FileNameFormatter.key_terms])
