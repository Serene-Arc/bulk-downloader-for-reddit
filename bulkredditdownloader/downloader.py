#!/usr/bin/env python3
# coding=utf-8

import argparse
import configparser
import logging
import socket
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

import appdirs
import praw
import praw.models

from bulkredditdownloader.download_filter import DownloadFilter
from bulkredditdownloader.errors import NotADownloadableLinkError, RedditAuthenticationError
from bulkredditdownloader.file_name_formatter import FileNameFormatter
from bulkredditdownloader.site_downloaders.download_factory import DownloadFactory

logger = logging.getLogger(__name__)


class RedditTypes:
    class SortType(Enum):
        HOT = auto()
        RISING = auto()
        CONTROVERSIAL = auto()
        NEW = auto()
        RELEVENCE = auto()

    class TimeType(Enum):
        HOUR = auto()
        DAY = auto()
        WEEK = auto()
        MONTH = auto()
        YEAR = auto()
        ALL = auto()


class RedditDownloader:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.config_directories = appdirs.AppDirs('bulk_reddit_downloader')
        self.run_time = datetime.now().isoformat()
        self._setup_internal_objects()

        self.reddit_lists = self._retrieve_reddit_lists()

    def _setup_internal_objects(self):
        self.download_filter = self._create_download_filter()
        self.time_filter = self._create_time_filter()
        self.sort_filter = self._create_sort_filter()
        self.file_name_formatter = self._create_file_name_formatter()
        self._determine_directories()
        self._create_file_logger()
        self.master_hash_list = []
        self._load_config()
        if self.cfg_parser.has_option('DEFAULT', 'username') and self.cfg_parser.has_option('DEFAULT', 'password'):
            self.authenticated = True

            self.reddit_instance = praw.Reddit(client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                                               client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                                               user_agent=socket.gethostname(),
                                               username=self.cfg_parser.get('DEFAULT', 'username'),
                                               password=self.cfg_parser.get('DEFAULT', 'password'))
        else:
            self.authenticated = False
            self.reddit_instance = praw.Reddit(client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                                               client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                                               user_agent=socket.gethostname())

    def _retrieve_reddit_lists(self) -> list[praw.models.ListingGenerator]:
        master_list = []
        master_list.extend(self._get_subreddits())
        master_list.extend(self._get_multireddits())
        master_list.extend(self._get_user_data())
        return master_list

    def _determine_directories(self):
        self.download_directory = Path(self.args.directory)
        self.logfile_directory = self.download_directory / 'LOG_FILES'
        self.config_directory = self.config_directories.user_config_dir

        self.download_directory.mkdir(exist_ok=True, parents=True)
        self.logfile_directory.mkdir(exist_ok=True, parents=True)

    def _load_config(self):
        self.cfg_parser = configparser.ConfigParser()
        if self.args.use_local_config and Path('./config.cfg').exists():
            self.cfg_parser.read(Path('./config.cfg'))
        else:
            self.cfg_parser.read(Path('./default_config.cfg').resolve())

    def _create_file_logger(self):
        main_logger = logging.getLogger()
        file_handler = logging.FileHandler(self.logfile_directory / 'log_output.txt')
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)

        main_logger.addHandler(file_handler)

    def _get_subreddits(self) -> list[praw.models.ListingGenerator]:
        if self.args.subreddit:
            subreddits = [self.reddit_instance.subreddit(chosen_subreddit) for chosen_subreddit in self.args.subreddit]
            if self.args.search:
                return [reddit.search(self.args.search, sort=self.sort_filter.name.lower()) for reddit in subreddits]
            else:
                sort_function = self._determine_sort_function()
                return [sort_function(reddit, limit=self.args.limit) for reddit in subreddits]
        else:
            return []

    def _determine_sort_function(self):
        if self.sort_filter is RedditTypes.SortType.NEW:
            sort_function = praw.models.Subreddit.new
        elif self.sort_filter is RedditTypes.SortType.RISING:
            sort_function = praw.models.Subreddit.rising
        elif self.sort_filter is RedditTypes.SortType.CONTROVERSIAL:
            sort_function = praw.models.Subreddit.controversial
        else:
            sort_function = praw.models.Subreddit.hot
        return sort_function

    def _get_multireddits(self) -> list[praw.models.ListingGenerator]:
        if self.args.multireddit:
            if self.authenticated:
                return [self.reddit_instance.multireddit(m_reddit_choice) for m_reddit_choice in self.args.multireddit]
            else:
                raise RedditAuthenticationError('Accessing multireddits requires authentication')
        else:
            return []

    def _get_user_data(self) -> list[praw.models.ListingGenerator]:
        if any((self.args.upvoted, self.args.submitted, self.args.saved)):
            if self.authenticated:
                generators = []
                sort_function = self._determine_sort_function()
                if self.args.upvoted:
                    generators.append(self.reddit_instance.redditor(self.args.user).upvoted)
                if self.args.submitted:
                    generators.append(
                        sort_function(
                            self.reddit_instance.redditor(self.args.user).submissions,
                            limit=self.args.limit))
                if self.args.saved:
                    generators.append(self.reddit_instance.redditor(self.args.user).saved)

                return generators
            else:
                raise RedditAuthenticationError('Accessing user lists requires authentication')
        else:
            return []

    def _create_file_name_formatter(self) -> FileNameFormatter:
        return FileNameFormatter(self.args.set_filename, self.args.set_folderpath)

    def _create_time_filter(self) -> RedditTypes.TimeType:
        try:
            return RedditTypes.TimeType[self.args.sort.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.TimeType.ALL

    def _create_sort_filter(self) -> RedditTypes.SortType:
        try:
            return RedditTypes.SortType[self.args.time.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.SortType.HOT

    def _create_download_filter(self) -> DownloadFilter:
        formats = {
            "videos": [".mp4", ".webm"],
            "images": [".jpg", ".jpeg", ".png", ".bmp"],
            "gifs": [".gif"],
            "self": []
        }
        excluded_extensions = [extension for ext_type in self.args.skip for extension in formats.get(ext_type, ())]
        return DownloadFilter(excluded_extensions, self.args.skip_domain)

    def download(self):
        for generator in self.reddit_lists:
            for submission in generator:
                self._download_submission(submission)

    def _download_submission(self, submission: praw.models.Submission):
        if self.download_filter.check_url(submission.url):
            try:
                downloader_class = DownloadFactory.pull_lever(submission.url)
                downloader = downloader_class(self.download_directory, submission)
                if self.args.no_download:
                    logger.info('Skipping download for submission {}'.format(submission.id))
                else:
                    content = downloader.download()
                    for res in content:
                        destination = self.file_name_formatter.format_path(res, self.download_directory)
                        if destination.exists():
                            logger.debug('File already exists: {}'.format(destination))
                        else:
                            if res.hash.hexdigest() not in self.master_hash_list and self.args.no_dupes:
                                # TODO: consider making a hard link/symlink here
                                destination.parent.mkdir(parents=True, exist_ok=True)
                                with open(destination, 'wb') as file:
                                    file.write(res.content)
                                logger.debug('Written file to {}'.format(destination))
                                self.master_hash_list.append(res.hash.hexdigest())
                                logger.debug('Hash added to master list: {}'.format(res.hash.hexdigest()))
                            else:
                                logger.debug(f'Resource from {res.url} downloaded elsewhere')

                logger.info('Downloaded submission {}'.format(submission.name))
            except NotADownloadableLinkError as e:
                logger.error('Could not download submission {}: {}'.format(submission.name, e))
