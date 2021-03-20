#!/usr/bin/env python3
# coding=utf-8

import configparser
import hashlib
import importlib.resources
import logging
import os
import re
import socket
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Iterator

import appdirs
import praw
import praw.exceptions
import praw.models
import prawcore

import bulkredditdownloader.exceptions as errors
from bulkredditdownloader.configuration import Configuration
from bulkredditdownloader.download_filter import DownloadFilter
from bulkredditdownloader.file_name_formatter import FileNameFormatter
from bulkredditdownloader.oauth2 import OAuth2Authenticator, OAuth2TokenManager
from bulkredditdownloader.site_authenticator import SiteAuthenticator
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
    def __init__(self, args: Configuration):
        self.args = args
        self.config_directories = appdirs.AppDirs('bulkredditdownloader', 'BDFR')
        self.run_time = datetime.now().isoformat()
        self._setup_internal_objects()

        self.reddit_lists = self._retrieve_reddit_lists()

    def _setup_internal_objects(self):
        self._determine_directories()
        self._create_file_logger()

        self.download_filter = self._create_download_filter()
        logger.log(9, 'Created download filter')
        self.time_filter = self._create_time_filter()
        logger.log(9, 'Created time filter')
        self.sort_filter = self._create_sort_filter()
        logger.log(9, 'Created sort filter')
        self.file_name_formatter = self._create_file_name_formatter()
        logger.log(9, 'Create file name formatter')

        self._load_config()
        logger.debug(f'Configuration loaded from {self.config_location}')
        self._create_reddit_instance()
        self._resolve_user_name()

        if self.args.search_existing:
            self.master_hash_list = self.scan_existing_files(self.download_directory)
        else:
            self.master_hash_list = {}
        self.authenticator = self._create_authenticator()
        logger.log(9, 'Created site authenticator')

    def _create_reddit_instance(self):
        if self.args.authenticate:
            logger.debug('Using authenticated Reddit instance')
            if not self.cfg_parser.has_option('DEFAULT', 'user_token'):
                logger.log(9, 'Commencing OAuth2 authentication')
                scopes = self.cfg_parser.get('DEFAULT', 'scopes')
                scopes = OAuth2Authenticator.split_scopes(scopes)
                oauth2_authenticator = OAuth2Authenticator(
                    scopes,
                    self.cfg_parser.get('DEFAULT', 'client_id'),
                    self.cfg_parser.get('DEFAULT', 'client_secret'))
                token = oauth2_authenticator.retrieve_new_token()
                self.cfg_parser['DEFAULT']['user_token'] = token
                with open(self.config_location, 'w') as file:
                    self.cfg_parser.write(file, True)
            token_manager = OAuth2TokenManager(self.cfg_parser, self.config_location)

            self.authenticated = True
            self.reddit_instance = praw.Reddit(client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                                               client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                                               user_agent=socket.gethostname(),
                                               token_manager=token_manager)
        else:
            logger.debug('Using unauthenticated Reddit instance')
            self.authenticated = False
            self.reddit_instance = praw.Reddit(client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                                               client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                                               user_agent=socket.gethostname())

    def _retrieve_reddit_lists(self) -> list[praw.models.ListingGenerator]:
        master_list = []
        master_list.extend(self._get_subreddits())
        logger.log(9, 'Retrieved subreddits')
        master_list.extend(self._get_multireddits())
        logger.log(9, 'Retrieved multireddits')
        master_list.extend(self._get_user_data())
        logger.log(9, 'Retrieved user data')
        master_list.extend(self._get_submissions_from_link())
        logger.log(9, 'Retrieved submissions for given links')
        return master_list

    def _determine_directories(self):
        self.download_directory = Path(self.args.directory).resolve().expanduser()
        self.config_directory = Path(self.config_directories.user_config_dir)

        self.download_directory.mkdir(exist_ok=True, parents=True)
        self.config_directory.mkdir(exist_ok=True, parents=True)

    def _load_config(self):
        self.cfg_parser = configparser.ConfigParser()
        if self.args.config:
            if (cfg_path := Path(self.args.config)).exists():
                self.cfg_parser.read(cfg_path)
                self.config_location = cfg_path
                return
            else:
                logger.error(f'Could not find config file at {self.args.config}, attempting to find elsewhere')
        possible_paths = [Path('./config.cfg'),
                          Path('./default_config.cfg'),
                          Path(self.config_directory, 'config.cfg'),
                          Path(self.config_directory, 'default_config.cfg'),
                          list(importlib.resources.path('bulkredditdownloader', 'default_config.cfg').gen)[0],
                          ]
        self.config_location = None
        for path in possible_paths:
            if path.resolve().expanduser().exists():
                self.config_location = path
                logger.debug(f'Loading configuration from {path}')
                break
        if not self.config_location:
            raise errors.BulkDownloaderException('Could not find a configuration file to load')
        self.cfg_parser.read(self.config_location)

    def _create_file_logger(self):
        main_logger = logging.getLogger()
        file_handler = logging.FileHandler(Path(self.config_directory, 'log_output.txt'), mode='w')
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)

        main_logger.addHandler(file_handler)

    @staticmethod
    def _sanitise_subreddit_name(subreddit: str) -> str:
        pattern = re.compile(r'^(?:https://www\.reddit\.com/)?(?:r/)?(.*?)(?:/)?$')
        match = re.match(pattern, subreddit)
        if not match:
            raise errors.BulkDownloaderException(f'Could not find subreddit name in string {subreddit}')
        return match.group(1)

    @staticmethod
    def _split_args_input(subreddit_entries: list[str]) -> set[str]:
        all_subreddits = []
        split_pattern = re.compile(r'[,;]\s?')
        for entry in subreddit_entries:
            results = re.split(split_pattern, entry)
            all_subreddits.extend([RedditDownloader._sanitise_subreddit_name(name) for name in results])
        return set(all_subreddits)

    def _get_subreddits(self) -> list[praw.models.ListingGenerator]:
        if self.args.subreddit:
            out = []
            sort_function = self._determine_sort_function()
            for reddit in self._split_args_input(self.args.subreddit):
                try:
                    reddit = self.reddit_instance.subreddit(reddit)
                    if self.args.search:
                        out.append(
                            reddit.search(
                                self.args.search,
                                sort=self.sort_filter.name.lower(),
                                limit=self.args.limit))
                        logger.debug(
                            f'Added submissions from subreddit {reddit} with the search term "{self.args.search}"')
                    else:
                        out.append(sort_function(reddit, limit=self.args.limit))
                        logger.debug(f'Added submissions from subreddit {reddit}')
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException) as e:
                    logger.error(f'Failed to get submissions for subreddit {reddit}: {e}')
            return out
        else:
            return []

    def _resolve_user_name(self):
        if self.args.user == 'me':
            if self.authenticated:
                self.args.user = self.reddit_instance.user.me().name
                logger.log(9, f'Resolved user to {self.args.user}')
            else:
                self.args.user = None
                logger.error('To use "me" as a user, an authenticated Reddit instance must be used')

    def _get_submissions_from_link(self) -> list[list[praw.models.Submission]]:
        supplied_submissions = []
        for sub_id in self.args.link:
            if len(sub_id) == 6:
                supplied_submissions.append(self.reddit_instance.submission(id=sub_id))
            else:
                supplied_submissions.append(self.reddit_instance.submission(url=sub_id))
        return [supplied_submissions]

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

    def _get_multireddits(self) -> list[Iterator]:
        if self.args.multireddit:
            out = []
            sort_function = self._determine_sort_function()
            for multi in self._split_args_input(self.args.multireddit):
                try:
                    multi = self.reddit_instance.multireddit(self.args.user, multi)
                    if not multi.subreddits:
                        raise errors.BulkDownloaderException
                    out.append(sort_function(multi, limit=self.args.limit))
                    logger.debug(f'Added submissions from multireddit {multi}')
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException, prawcore.PrawcoreException) as e:
                    logger.error(f'Failed to get submissions for multireddit {multi}: {e}')
            return out
        else:
            return []

    def _get_user_data(self) -> list[Iterator]:
        if any([self.args.submitted, self.args.upvoted, self.args.saved]):
            if self.args.user:
                if not self._check_user_existence(self.args.user):
                    logger.error(f'User {self.args.user} does not exist')
                    return []
                generators = []
                sort_function = self._determine_sort_function()
                if self.args.submitted:
                    logger.debug(f'Retrieving submitted posts of user {self.args.user}')
                    generators.append(
                        sort_function(
                            self.reddit_instance.redditor(self.args.user).submissions, limit=self.args.limit))
                if not self.authenticated and any((self.args.upvoted, self.args.saved)):
                    logger.error('Accessing user lists requires authentication')
                else:
                    if self.args.upvoted:
                        logger.debug(f'Retrieving upvoted posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(self.args.user).upvoted(limit=self.args.limit))
                    if self.args.saved:
                        logger.debug(f'Retrieving saved posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(self.args.user).saved(limit=self.args.limit))
                return generators
            else:
                logger.error('A user must be supplied to download user data')
                return []
        else:
            return []

    def _check_user_existence(self, name: str) -> bool:
        user = self.reddit_instance.redditor(name=name)
        try:
            if not user.id:
                return False
        except prawcore.exceptions.NotFound:
            return False
        return True

    def _create_file_name_formatter(self) -> FileNameFormatter:
        return FileNameFormatter(self.args.file_scheme, self.args.folder_scheme)

    def _create_time_filter(self) -> RedditTypes.TimeType:
        try:
            return RedditTypes.TimeType[self.args.time.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.TimeType.ALL

    def _create_sort_filter(self) -> RedditTypes.SortType:
        try:
            return RedditTypes.SortType[self.args.sort.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.SortType.HOT

    def _create_download_filter(self) -> DownloadFilter:
        return DownloadFilter(self.args.skip, self.args.skip_domain)

    def _create_authenticator(self) -> SiteAuthenticator:
        return SiteAuthenticator(self.cfg_parser)

    def download(self):
        for generator in self.reddit_lists:
            for submission in generator:
                logger.debug(f'Attempting to download submission {submission.id}')
                self._download_submission(submission)

    def _download_submission(self, submission: praw.models.Submission):
        if not self.download_filter.check_url(submission.url):
            logger.debug(f'Download filter removed submission {submission.id} with URL {submission.url}')
            return
        try:
            downloader_class = DownloadFactory.pull_lever(submission.url)
            downloader = downloader_class(submission)
            logger.debug(f'Using {downloader_class.__name__} with url {submission.url}')
        except errors.NotADownloadableLinkError as e:
            logger.error(f'Could not download submission {submission.name}: {e}')
            return

        try:
            content = downloader.find_resources(self.authenticator)
        except errors.SiteDownloaderError:
            logger.error(f'Site {downloader_class.__name__} failed to download submission {submission.id}')
            return
        for destination, res in self.file_name_formatter.format_resource_paths(content, self.download_directory):
            if destination.exists():
                logger.warning(f'File already exists: {destination}')
            else:
                try:
                    res.download()
                except errors.BulkDownloaderException:
                    logger.error(
                        f'Failed to download resource from {res.url} with downloader {downloader_class.__name__}')
                    return
                resource_hash = res.hash.hexdigest()
                if resource_hash in self.master_hash_list:
                    if self.args.no_dupes:
                        logger.warning(f'Resource from "{res.url}" and hash "{resource_hash}" downloaded elsewhere')
                        return
                    elif self.args.make_hard_links:
                        self.master_hash_list[resource_hash].link_to(destination)
                        logger.debug(
                            f'Hard link made linking {destination} to {self.master_hash_list[resource_hash]}')
                        return
                destination.parent.mkdir(parents=True, exist_ok=True)
                with open(destination, 'wb') as file:
                    file.write(res.content)
                logger.debug(f'Written file to {destination}')
                self.master_hash_list[resource_hash] = destination
                logger.debug(f'Hash added to master list: {resource_hash}')
                logger.info(f'Downloaded submission {submission.id} from {submission.subreddit.display_name}')

    @staticmethod
    def scan_existing_files(directory: Path) -> dict[str, Path]:
        files = []
        for (dirpath, dirnames, filenames) in os.walk(directory):
            files.extend([Path(dirpath, file) for file in filenames])
        logger.info(f'Calculating hashes for {len(files)} files')
        hash_list = {}
        for existing_file in files:
            with open(existing_file, 'rb') as file:
                hash_list[hashlib.md5(file.read()).hexdigest()] = existing_file
                logger.log(9, f'Hash calculated for file at {existing_file}')
        return hash_list
