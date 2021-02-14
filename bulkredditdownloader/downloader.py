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
        self.config_directories = appdirs.AppDirs('bulk_reddit_downloader')
        self.run_time = datetime.now().isoformat()
        self._setup_internal_objects(args)

        self.reddit_lists = self._retrieve_reddit_lists(args)

    def _setup_internal_objects(self, args: argparse.Namespace):
        self.download_filter = RedditDownloader._create_download_filter(args)
        self.time_filter = RedditDownloader._create_time_filter(args)
        self.sort_filter = RedditDownloader._create_sort_filter(args)
        self.file_name_formatter = RedditDownloader._create_file_name_formatter(args)
        self._determine_directories(args)
        self._create_file_logger()
        self.master_hash_list = []
        self._load_config(args)
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

    def _retrieve_reddit_lists(self, args: argparse.Namespace) -> list[praw.models.ListingGenerator]:
        master_list = []
        master_list.extend(self._get_subreddits(args))
        master_list.extend(self._get_multireddits(args))
        master_list.extend(self._get_user_data(args))
        return master_list

    def _determine_directories(self, args: argparse.Namespace):
        self.download_directory = Path(args.directory)
        self.logfile_directory = self.download_directory / 'LOG_FILES'
        self.config_directory = self.config_directories.user_config_dir

    def _load_config(self, args: argparse.Namespace):
        self.cfg_parser = configparser.ConfigParser()
        if args.use_local_config and Path('./config.cfg').exists():
            self.cfg_parser.read(Path('./config.cfg'))
        else:
            self.cfg_parser.read(Path('./default_config.cfg').resolve())

    def _create_file_logger(self):
        main_logger = logging.getLogger()
        file_handler = logging.FileHandler(self.logfile_directory)
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)

        main_logger.addHandler(file_handler)

    def _get_subreddits(self, args: argparse.Namespace) -> list[praw.models.ListingGenerator]:
        if args.subreddit:
            subreddits = [self.reddit_instance.subreddit(chosen_subreddit) for chosen_subreddit in args.subreddit]
            if args.search:
                return [reddit.search(args.search, sort=self.sort_filter.name.lower()) for reddit in subreddits]
            else:
                if self.sort_filter is RedditTypes.SortType.NEW:
                    sort_function = praw.models.Subreddit.new
                elif self.sort_filter is RedditTypes.SortType.RISING:
                    sort_function = praw.models.Subreddit.rising
                elif self.sort_filter is RedditTypes.SortType.CONTROVERSIAL:
                    sort_function = praw.models.Subreddit.controversial
                else:
                    sort_function = praw.models.Subreddit.hot
                return [sort_function(reddit) for reddit in subreddits]
        else:
            return []

    def _get_multireddits(self, args: argparse.Namespace) -> list[praw.models.ListingGenerator]:
        if args.multireddit:
            if self.authenticated:
                return [self.reddit_instance.multireddit(m_reddit_choice) for m_reddit_choice in args.multireddit]
            else:
                raise RedditAuthenticationError('Accessing multireddits requires authentication')
        else:
            return []

    def _get_user_data(self, args: argparse.Namespace) -> list[praw.models.ListingGenerator]:
        if any((args.upvoted, args.submitted, args.saved)):
            if self.authenticated:
                generators = []
                if args.upvoted:
                    generators.append(self.reddit_instance.redditor(args.user).upvoted)
                if args.submitted:
                    generators.append(self.reddit_instance.redditor(args.user).submissions)
                if args.saved:
                    generators.append(self.reddit_instance.redditor(args.user).saved)

                return generators
            else:
                raise RedditAuthenticationError('Accessing user lists requires authentication')
        else:
            return []

    @staticmethod
    def _create_file_name_formatter(args: argparse.Namespace) -> FileNameFormatter:
        return FileNameFormatter(args.set_filename, args.set_folderpath)

    @staticmethod
    def _create_time_filter(args: argparse.Namespace) -> RedditTypes.TimeType:
        try:
            return RedditTypes.TimeType[args.sort.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.TimeType.ALL

    @staticmethod
    def _create_sort_filter(args: argparse.Namespace) -> RedditTypes.SortType:
        try:
            return RedditTypes.SortType[args.time.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.SortType.HOT

    @staticmethod
    def _create_download_filter(args: argparse.Namespace) -> DownloadFilter:
        formats = {
            "videos": [".mp4", ".webm"],
            "images": [".jpg", ".jpeg", ".png", ".bmp"],
            "gifs": [".gif"],
            "self": []
        }
        excluded_extensions = [extension for ext_type in args.skip for extension in formats.get(ext_type, ())]
        return DownloadFilter(excluded_extensions, args.skip_domain)

    def download(self):
        for generator in self.reddit_lists:
            for submission in generator:
                self._download_submission(submission)

    def _download_submission(self, submission: praw.models.Submission):
        if self.download_filter.check_url(submission.url):
            try:
                downloader_class = DownloadFactory.pull_lever(submission.url)
                downloader = downloader_class(self.download_directory, submission)
                content = downloader.download()
                for res in content:
                    destination = self.file_name_formatter.format_path(res, self.download_directory)
                    if destination.exists():
                        logger.debug('File already exists: {}'.format(destination))
                    else:
                        if res.hash.hexdigest() not in self.master_hash_list:
                            # TODO: consider making a hard link/symlink here
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            with open(destination, 'wb') as file:
                                file.write(res.content)
                            logger.debug('Written file to {}'.format(destination))
                            self.master_hash_list.append(res.hash.hexdigest())
                            logger.debug('Hash added to master list: {}'.format(res.hash.hexdigest()))

                logger.info('Downloaded submission {}'.format(submission.name))
            except NotADownloadableLinkError as e:
                logger.error('Could not download submission {}: {}'.format(submission.name, e))
