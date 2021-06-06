#!/usr/bin/env python3
# coding=utf-8

import configparser
import importlib.resources
import logging
import logging.handlers
import re
import shutil
import socket
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Iterator

import appdirs
import praw
import praw.exceptions
import praw.models
import prawcore

from bdfr import exceptions as errors
from bdfr.configuration import Configuration
from bdfr.download_filter import DownloadFilter
from bdfr.file_name_formatter import FileNameFormatter
from bdfr.oauth2 import OAuth2Authenticator, OAuth2TokenManager
from bdfr.site_authenticator import SiteAuthenticator

logger = logging.getLogger(__name__)


class RedditTypes:
    class SortType(Enum):
        CONTROVERSIAL = auto()
        HOT = auto()
        NEW = auto()
        RELEVENCE = auto()
        RISING = auto()
        TOP = auto()

    class TimeType(Enum):
        ALL = 'all'
        DAY = 'day'
        HOUR = 'hour'
        MONTH = 'month'
        WEEK = 'week'
        YEAR = 'year'


class RedditConnector(metaclass=ABCMeta):
    def __init__(self, args: Configuration):
        self.args = args
        self.config_directories = appdirs.AppDirs('bdfr', 'BDFR')
        self.run_time = datetime.now().isoformat()
        self._setup_internal_objects()

        self.reddit_lists = self.retrieve_reddit_lists()

    def _setup_internal_objects(self):
        self.determine_directories()
        self.load_config()
        self.create_file_logger()

        self.read_config()

        self.parse_disabled_modules()

        self.download_filter = self.create_download_filter()
        logger.log(9, 'Created download filter')
        self.time_filter = self.create_time_filter()
        logger.log(9, 'Created time filter')
        self.sort_filter = self.create_sort_filter()
        logger.log(9, 'Created sort filter')
        self.file_name_formatter = self.create_file_name_formatter()
        logger.log(9, 'Create file name formatter')

        self.create_reddit_instance()
        self.args.user = list(filter(None, [self.resolve_user_name(user) for user in self.args.user]))

        self.excluded_submission_ids = self.read_excluded_ids()

        self.master_hash_list = {}
        self.authenticator = self.create_authenticator()
        logger.log(9, 'Created site authenticator')

        self.args.skip_subreddit = self.split_args_input(self.args.skip_subreddit)
        self.args.skip_subreddit = set([sub.lower() for sub in self.args.skip_subreddit])

    def read_config(self):
        """Read any cfg values that need to be processed"""
        if self.args.max_wait_time is None:
            if not self.cfg_parser.has_option('DEFAULT', 'max_wait_time'):
                self.cfg_parser.set('DEFAULT', 'max_wait_time', '120')
                logger.log(9, 'Wrote default download wait time download to config file')
            self.args.max_wait_time = self.cfg_parser.getint('DEFAULT', 'max_wait_time')
            logger.debug(f'Setting maximum download wait time to {self.args.max_wait_time} seconds')
        if self.args.time_format is None:
            option = self.cfg_parser.get('DEFAULT', 'time_format', fallback='ISO')
            if re.match(r'^[ \'\"]*$', option):
                option = 'ISO'
            logger.debug(f'Setting datetime format string to {option}')
            self.args.time_format = option
        if not self.args.disable_module:
            self.args.disable_module = [self.cfg_parser.get('DEFAULT', 'disabled_modules', fallback='')]
        # Update config on disk
        with open(self.config_location, 'w') as file:
            self.cfg_parser.write(file)

    def parse_disabled_modules(self):
        disabled_modules = self.args.disable_module
        disabled_modules = self.split_args_input(disabled_modules)
        disabled_modules = set([name.strip().lower() for name in disabled_modules])
        self.args.disable_module = disabled_modules
        logger.debug(f'Disabling the following modules: {", ".join(self.args.disable_module)}')

    def create_reddit_instance(self):
        if self.args.authenticate:
            logger.debug('Using authenticated Reddit instance')
            if not self.cfg_parser.has_option('DEFAULT', 'user_token'):
                logger.log(9, 'Commencing OAuth2 authentication')
                scopes = self.cfg_parser.get('DEFAULT', 'scopes')
                scopes = OAuth2Authenticator.split_scopes(scopes)
                oauth2_authenticator = OAuth2Authenticator(
                    scopes,
                    self.cfg_parser.get('DEFAULT', 'client_id'),
                    self.cfg_parser.get('DEFAULT', 'client_secret'),
                )
                token = oauth2_authenticator.retrieve_new_token()
                self.cfg_parser['DEFAULT']['user_token'] = token
                with open(self.config_location, 'w') as file:
                    self.cfg_parser.write(file, True)
            token_manager = OAuth2TokenManager(self.cfg_parser, self.config_location)

            self.authenticated = True
            self.reddit_instance = praw.Reddit(
                client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                user_agent=socket.gethostname(),
                token_manager=token_manager,
            )
        else:
            logger.debug('Using unauthenticated Reddit instance')
            self.authenticated = False
            self.reddit_instance = praw.Reddit(
                client_id=self.cfg_parser.get('DEFAULT', 'client_id'),
                client_secret=self.cfg_parser.get('DEFAULT', 'client_secret'),
                user_agent=socket.gethostname(),
            )

    def retrieve_reddit_lists(self) -> list[praw.models.ListingGenerator]:
        master_list = []
        master_list.extend(self.get_subreddits())
        logger.log(9, 'Retrieved subreddits')
        master_list.extend(self.get_multireddits())
        logger.log(9, 'Retrieved multireddits')
        master_list.extend(self.get_user_data())
        logger.log(9, 'Retrieved user data')
        master_list.extend(self.get_submissions_from_link())
        logger.log(9, 'Retrieved submissions for given links')
        return master_list

    def determine_directories(self):
        self.download_directory = Path(self.args.directory).resolve().expanduser()
        self.config_directory = Path(self.config_directories.user_config_dir)

        self.download_directory.mkdir(exist_ok=True, parents=True)
        self.config_directory.mkdir(exist_ok=True, parents=True)

    def load_config(self):
        self.cfg_parser = configparser.ConfigParser()
        if self.args.config:
            if (cfg_path := Path(self.args.config)).exists():
                self.cfg_parser.read(cfg_path)
                self.config_location = cfg_path
                return
        possible_paths = [
            Path('./config.cfg'),
            Path('./default_config.cfg'),
            Path(self.config_directory, 'config.cfg'),
            Path(self.config_directory, 'default_config.cfg'),
        ]
        self.config_location = None
        for path in possible_paths:
            if path.resolve().expanduser().exists():
                self.config_location = path
                logger.debug(f'Loading configuration from {path}')
                break
        if not self.config_location:
            self.config_location = list(importlib.resources.path('bdfr', 'default_config.cfg').gen)[0]
            shutil.copy(self.config_location, Path(self.config_directory, 'default_config.cfg'))
        if not self.config_location:
            raise errors.BulkDownloaderException('Could not find a configuration file to load')
        self.cfg_parser.read(self.config_location)

    def create_file_logger(self):
        main_logger = logging.getLogger()
        if self.args.log is None:
            log_path = Path(self.config_directory, 'log_output.txt')
        else:
            log_path = Path(self.args.log).resolve().expanduser()
            if not log_path.parent.exists():
                raise errors.BulkDownloaderException(f'Designated location for logfile does not exist')
        backup_count = self.cfg_parser.getint('DEFAULT', 'backup_log_count', fallback=3)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            mode='a',
            backupCount=backup_count,
        )
        if log_path.exists():
            try:
                file_handler.doRollover()
            except PermissionError as e:
                logger.critical(
                    'Cannot rollover logfile, make sure this is the only '
                    'BDFR process or specify alternate logfile location')
                raise
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)

        main_logger.addHandler(file_handler)

    @staticmethod
    def sanitise_subreddit_name(subreddit: str) -> str:
        pattern = re.compile(r'^(?:https://www\.reddit\.com/)?(?:r/)?(.*?)/?$')
        match = re.match(pattern, subreddit)
        if not match:
            raise errors.BulkDownloaderException(f'Could not find subreddit name in string {subreddit}')
        return match.group(1)

    @staticmethod
    def split_args_input(entries: list[str]) -> set[str]:
        all_entries = []
        split_pattern = re.compile(r'[,;]\s?')
        for entry in entries:
            results = re.split(split_pattern, entry)
            all_entries.extend([RedditConnector.sanitise_subreddit_name(name) for name in results])
        return set(all_entries)

    def get_subreddits(self) -> list[praw.models.ListingGenerator]:
        if self.args.subreddit:
            out = []
            for reddit in self.split_args_input(self.args.subreddit):
                try:
                    reddit = self.reddit_instance.subreddit(reddit)
                    try:
                        self.check_subreddit_status(reddit)
                    except errors.BulkDownloaderException as e:
                        logger.error(e)
                        continue
                    if self.args.search:
                        out.append(reddit.search(
                            self.args.search,
                            sort=self.sort_filter.name.lower(),
                            limit=self.args.limit,
                            time_filter=self.time_filter.value,
                        ))
                        logger.debug(
                            f'Added submissions from subreddit {reddit} with the search term "{self.args.search}"')
                    else:
                        out.append(self.create_filtered_listing_generator(reddit))
                        logger.debug(f'Added submissions from subreddit {reddit}')
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException) as e:
                    logger.error(f'Failed to get submissions for subreddit {reddit}: {e}')
            return out
        else:
            return []

    def resolve_user_name(self, in_name: str) -> str:
        if in_name == 'me':
            if self.authenticated:
                resolved_name = self.reddit_instance.user.me().name
                logger.log(9, f'Resolved user to {resolved_name}')
                return resolved_name
            else:
                logger.warning('To use "me" as a user, an authenticated Reddit instance must be used')
        else:
            return in_name

    def get_submissions_from_link(self) -> list[list[praw.models.Submission]]:
        supplied_submissions = []
        for sub_id in self.args.link:
            if len(sub_id) == 6:
                supplied_submissions.append(self.reddit_instance.submission(id=sub_id))
            else:
                supplied_submissions.append(self.reddit_instance.submission(url=sub_id))
        return [supplied_submissions]

    def determine_sort_function(self) -> Callable:
        if self.sort_filter is RedditTypes.SortType.NEW:
            sort_function = praw.models.Subreddit.new
        elif self.sort_filter is RedditTypes.SortType.RISING:
            sort_function = praw.models.Subreddit.rising
        elif self.sort_filter is RedditTypes.SortType.CONTROVERSIAL:
            sort_function = praw.models.Subreddit.controversial
        elif self.sort_filter is RedditTypes.SortType.TOP:
            sort_function = praw.models.Subreddit.top
        else:
            sort_function = praw.models.Subreddit.hot
        return sort_function

    def get_multireddits(self) -> list[Iterator]:
        if self.args.multireddit:
            if len(self.args.user) != 1:
                logger.error(f'Only 1 user can be supplied when retrieving from multireddits')
                return []
            out = []
            for multi in self.split_args_input(self.args.multireddit):
                try:
                    multi = self.reddit_instance.multireddit(self.args.user[0], multi)
                    if not multi.subreddits:
                        raise errors.BulkDownloaderException
                    out.append(self.create_filtered_listing_generator(multi))
                    logger.debug(f'Added submissions from multireddit {multi}')
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException, prawcore.PrawcoreException) as e:
                    logger.error(f'Failed to get submissions for multireddit {multi}: {e}')
            return out
        else:
            return []

    def create_filtered_listing_generator(self, reddit_source) -> Iterator:
        sort_function = self.determine_sort_function()
        if self.sort_filter in (RedditTypes.SortType.TOP, RedditTypes.SortType.CONTROVERSIAL):
            return sort_function(reddit_source, limit=self.args.limit, time_filter=self.time_filter.value)
        else:
            return sort_function(reddit_source, limit=self.args.limit)

    def get_user_data(self) -> list[Iterator]:
        if any([self.args.submitted, self.args.upvoted, self.args.saved]):
            if not self.args.user:
                logger.warning('At least one user must be supplied to download user data')
                return []
            generators = []
            for user in self.args.user:
                try:
                    self.check_user_existence(user)
                except errors.BulkDownloaderException as e:
                    logger.error(e)
                    continue
                if self.args.submitted:
                    logger.debug(f'Retrieving submitted posts of user {self.args.user}')
                    generators.append(self.create_filtered_listing_generator(
                        self.reddit_instance.redditor(user).submissions,
                    ))
                if not self.authenticated and any((self.args.upvoted, self.args.saved)):
                    logger.warning('Accessing user lists requires authentication')
                else:
                    if self.args.upvoted:
                        logger.debug(f'Retrieving upvoted posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(user).upvoted(limit=self.args.limit))
                    if self.args.saved:
                        logger.debug(f'Retrieving saved posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(user).saved(limit=self.args.limit))
            return generators
        else:
            return []

    def check_user_existence(self, name: str):
        user = self.reddit_instance.redditor(name=name)
        try:
            if user.id:
                return
        except prawcore.exceptions.NotFound:
            raise errors.BulkDownloaderException(f'Could not find user {name}')
        except AttributeError:
            if hasattr(user, 'is_suspended'):
                raise errors.BulkDownloaderException(f'User {name} is banned')

    def create_file_name_formatter(self) -> FileNameFormatter:
        return FileNameFormatter(self.args.file_scheme, self.args.folder_scheme, self.args.time_format)

    def create_time_filter(self) -> RedditTypes.TimeType:
        try:
            return RedditTypes.TimeType[self.args.time.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.TimeType.ALL

    def create_sort_filter(self) -> RedditTypes.SortType:
        try:
            return RedditTypes.SortType[self.args.sort.upper()]
        except (KeyError, AttributeError):
            return RedditTypes.SortType.HOT

    def create_download_filter(self) -> DownloadFilter:
        return DownloadFilter(self.args.skip, self.args.skip_domain)

    def create_authenticator(self) -> SiteAuthenticator:
        return SiteAuthenticator(self.cfg_parser)

    @abstractmethod
    def download(self):
        pass

    @staticmethod
    def check_subreddit_status(subreddit: praw.models.Subreddit):
        if subreddit.display_name == 'all':
            return
        try:
            assert subreddit.id
        except prawcore.NotFound:
            raise errors.BulkDownloaderException(f'Source {subreddit.display_name} does not exist or cannot be found')
        except prawcore.Forbidden:
            raise errors.BulkDownloaderException(f'Source {subreddit.display_name} is private and cannot be scraped')

    def read_excluded_ids(self) -> set[str]:
        out = []
        out.extend(self.args.exclude_id)
        for id_file in self.args.exclude_id_file:
            id_file = Path(id_file).resolve().expanduser()
            if not id_file.exists():
                logger.warning(f'ID exclusion file at {id_file} does not exist')
                continue
            with open(id_file, 'r') as file:
                for line in file:
                    out.append(line.strip())
        return set(out)
