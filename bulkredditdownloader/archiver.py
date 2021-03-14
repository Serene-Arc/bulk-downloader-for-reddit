#!/usr/bin/env python3
# coding=utf-8

import json
import logging

import dict2xml
import praw.models
import yaml

from bulkredditdownloader.archive_entry import ArchiveEntry
from bulkredditdownloader.configuration import Configuration
from bulkredditdownloader.downloader import RedditDownloader
from bulkredditdownloader.exceptions import ArchiverError
from bulkredditdownloader.resource import Resource

logger = logging.getLogger(__name__)


class Archiver(RedditDownloader):
    def __init__(self, args: Configuration):
        super(Archiver, self).__init__(args)

    def download(self):
        for generator in self.reddit_lists:
            for submission in generator:
                logger.debug(f'Attempting to archive submission {submission.id}')
                self._write_submission(submission)

    def _write_submission(self, submission: praw.models.Submission):
        archive_entry = ArchiveEntry(submission)
        if self.args.format == 'json':
            self._write_submission_json(archive_entry)
        elif self.args.format == 'xml':
            self._write_submission_xml(archive_entry)
        elif self.args.format == 'yaml':
            self._write_submission_yaml(archive_entry)
        else:
            raise ArchiverError(f'Unknown format {self.args.format} given')
        logger.info(f'Record for submission {submission.id} written to disk')

    def _write_submission_json(self, entry: ArchiveEntry):
        resource = Resource(entry.submission, '', '.json')
        file_path = self.file_name_formatter.format_path(resource, self.download_directory)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w') as file:
            logger.debug(f'Writing submission {entry.submission.id} to file in JSON format at {file_path}')
            json.dump(entry.compile(), file)

    def _write_submission_xml(self, entry: ArchiveEntry):
        resource = Resource(entry.submission, '', '.xml')
        file_path = self.file_name_formatter.format_path(resource, self.download_directory)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w') as file:
            logger.debug(f'Writing submission {entry.submission.id} to file in XML format at {file_path}')
            xml_entry = dict2xml.dict2xml(entry.compile(), wrap='root')
            file.write(xml_entry)

    def _write_submission_yaml(self, entry: ArchiveEntry):
        resource = Resource(entry.submission, '', '.yaml')
        file_path = self.file_name_formatter.format_path(resource, self.download_directory)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w') as file:
            logger.debug(f'Writing submission {entry.submission.id} to file in YAML format at {file_path}')
            yaml.dump(entry.compile(), file)
