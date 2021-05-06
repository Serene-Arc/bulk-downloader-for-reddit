#!/usr/bin/env python3
# coding=utf-8

import json
import logging
import re
from typing import Iterator

import dict2xml
import praw.models
import yaml

from bdfr.archive_entry.base_archive_entry import BaseArchiveEntry
from bdfr.archive_entry.comment_archive_entry import CommentArchiveEntry
from bdfr.archive_entry.submission_archive_entry import SubmissionArchiveEntry
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader
from bdfr.exceptions import ArchiverError
from bdfr.resource import Resource

logger = logging.getLogger(__name__)


class Archiver(RedditDownloader):
    def __init__(self, args: Configuration):
        super(Archiver, self).__init__(args)

    def download(self):
        for generator in self.reddit_lists:
            for submission in generator:
                logger.debug(f'Attempting to archive submission {submission.id}')
                self._write_entry(submission)

    def _get_submissions_from_link(self) -> list[list[praw.models.Submission]]:
        supplied_submissions = []
        for sub_id in self.args.link:
            if len(sub_id) == 6:
                supplied_submissions.append(self.reddit_instance.submission(id=sub_id))
            elif re.match(r'^\w{7}$', sub_id):
                supplied_submissions.append(self.reddit_instance.comment(id=sub_id))
            else:
                supplied_submissions.append(self.reddit_instance.submission(url=sub_id))
        return [supplied_submissions]

    def _get_user_data(self) -> list[Iterator]:
        results = super(Archiver, self)._get_user_data()
        if self.args.user and self.args.all_comments:
            sort = self._determine_sort_function()
            logger.debug(f'Retrieving comments of user {self.args.user}')
            results.append(sort(self.reddit_instance.redditor(self.args.user).comments, limit=self.args.limit))
        return results

    @staticmethod
    def _pull_lever_entry_factory(praw_item: (praw.models.Submission, praw.models.Comment)) -> BaseArchiveEntry:
        if isinstance(praw_item, praw.models.Submission):
            return SubmissionArchiveEntry(praw_item)
        elif isinstance(praw_item, praw.models.Comment):
            return CommentArchiveEntry(praw_item)
        else:
            raise ArchiverError(f'Factory failed to classify item of type {type(praw_item).__name__}')

    def _write_entry(self, praw_item: (praw.models.Submission, praw.models.Comment)):
        archive_entry = self._pull_lever_entry_factory(praw_item)
        if self.args.format == 'json':
            self._write_entry_json(archive_entry)
        elif self.args.format == 'xml':
            self._write_entry_xml(archive_entry)
        elif self.args.format == 'yaml':
            self._write_entry_yaml(archive_entry)
        else:
            raise ArchiverError(f'Unknown format {self.args.format} given')
        logger.info(f'Record for entry item {praw_item.id} written to disk')

    def _write_entry_json(self, entry: BaseArchiveEntry):
        resource = Resource(entry.source, '', '.json')
        content = json.dumps(entry.compile())
        self._write_content_to_disk(resource, content)

    def _write_entry_xml(self, entry: BaseArchiveEntry):
        resource = Resource(entry.source, '', '.xml')
        content = dict2xml.dict2xml(entry.compile(), wrap='root')
        self._write_content_to_disk(resource, content)

    def _write_entry_yaml(self, entry: BaseArchiveEntry):
        resource = Resource(entry.source, '', '.yaml')
        content = yaml.dump(entry.compile())
        self._write_content_to_disk(resource, content)

    def _write_content_to_disk(self, resource: Resource, content: str):
        file_path = self.file_name_formatter.format_path(resource, self.download_directory)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w', encoding="utf-8") as file:
            logger.debug(
                f'Writing entry {resource.source_submission.id} to file in {resource.extension[1:].upper()}'
                f' format at {file_path}')
            file.write(content)
