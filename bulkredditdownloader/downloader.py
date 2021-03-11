#!/usr/bin/env python3
# coding=utf-8

import configparser
import logging
import re
import socket
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Iterator

import appdirs
import praw
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
        self.config_directories = appdirs.AppDirs('bulk_reddit_downloader', 'BDFR')
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

        self._resolve_user_name()
        self._load_config()
        logger.debug(f'Configuration loaded from {self.config_location}')

        self.master_hash_list = []
        self.authenticator = self._create_authenticator()
        logger.log(9, 'Created site authenticator')
        self._create_reddit_instance()

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
        self.download_directory = Path(self.args.directory)
        self.logfile_directory = self.download_directory / 'LOG_FILES'
        self.config_directory = self.config_directories.user_config_dir

        self.download_directory.mkdir(exist_ok=True, parents=True)
        self.logfile_directory.mkdir(exist_ok=True, parents=True)

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
                          Path(self.config_directory, 'config.cfg'),
                          Path('./default_config.cfg'),
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
        file_handler = logging.FileHandler(self.logfile_directory / 'log_output.txt')
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)

        main_logger.addHandler(file_handler)

    @staticmethod
    def _sanitise_subreddit_name(subreddit: str) -> str:
        pattern = re.compile(r'^(?:https://www\.reddit\.com/)?(?:r/)?(.*?)(?:/)?$')
        match = re.match(pattern, subreddit)
        if not match:
            raise errors.RedditAuthenticationError('')
        return match.group(1)

    def _get_subreddits(self) -> list[praw.models.ListingGenerator]:
        if self.args.subreddit:
            subreddits = [self._sanitise_subreddit_name(subreddit) for subreddit in self.args.subreddit]
            subreddits = [self.reddit_instance.subreddit(chosen_subreddit) for chosen_subreddit in subreddits]
            if self.args.search:
                return [
                    reddit.search(
                        self.args.search,
                        sort=self.sort_filter.name.lower(),
                        limit=self.args.limit) for reddit in subreddits]
            else:
                sort_function = self._determine_sort_function()
                return [sort_function(reddit, limit=self.args.limit) for reddit in subreddits]
        else:
            return []

    def _resolve_user_name(self):
        if self.args.user == 'me':
            self.args.user = self.reddit_instance.user.me().name
            logger.log(9, f'Resolved user to {self.args.user}')

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
            if self.authenticated:
                if self.args.user:
                    sort_function = self._determine_sort_function()
                    multireddits = [self._sanitise_subreddit_name(multi) for multi in self.args.multireddit]
                    return [
                        sort_function(self.reddit_instance.multireddit(
                            self.args.user,
                            m_reddit_choice), limit=self.args.limit) for m_reddit_choice in multireddits]
                else:
                    raise errors.BulkDownloaderException('A user must be provided to download a multireddit')
            else:
                raise errors.RedditAuthenticationError('Accessing multireddits requires authentication')
        else:
            return []

    def _get_user_data(self) -> list[Iterator]:
        if any([self.args.submitted, self.args.upvoted, self.args.saved]):
            if self.args.user:
                if not self._check_user_existence(self.args.user):
                    raise errors.RedditUserError(f'User {self.args.user} does not exist')
                generators = []
                sort_function = self._determine_sort_function()
                if self.args.submitted:
                    logger.debug(f'Retrieving submitted posts of user {self.args.user}')
                    generators.append(
                        sort_function(
                            self.reddit_instance.redditor(self.args.user).submissions,
                            limit=self.args.limit))
                if not self.authenticated and any((self.args.upvoted, self.args.saved)):
                    raise errors.RedditAuthenticationError('Accessing user lists requires authentication')
                else:
                    if self.args.upvoted:
                        logger.debug(f'Retrieving upvoted posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(self.args.user).upvoted(limit=self.args.limit))
                    if self.args.saved:
                        logger.debug(f'Retrieving saved posts of user {self.args.user}')
                        generators.append(self.reddit_instance.redditor(self.args.user).saved(limit=self.args.limit))
                return generators
            else:
                raise errors.BulkDownloaderException('A user must be supplied to download user data')
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
        return FileNameFormatter(self.args.set_file_scheme, self.args.set_folder_scheme)

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
        if self.download_filter.check_url(submission.url):

            try:
                downloader_class = DownloadFactory.pull_lever(submission.url)
                downloader = downloader_class(submission)
            except errors.NotADownloadableLinkError as e:
                logger.error(f'Could not download submission {submission.name}: {e}')
                return

            content = downloader.find_resources(self.authenticator)
            for destination, res in self.file_name_formatter.format_resource_paths(content, self.download_directory):
                if destination.exists():
                    logger.warning(f'File already exists: {destination}')
                else:
                    res.download()
                    if res.hash.hexdigest() in self.master_hash_list and self.args.no_dupes:
                        logger.warning(
                            f'Resource from "{res.url}" and hash "{res.hash.hexdigest()}" downloaded elsewhere')
                    else:
                        # TODO: consider making a hard link/symlink here
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with open(destination, 'wb') as file:
                            file.write(res.content)
                        logger.debug(f'Written file to {destination}')
                        self.master_hash_list.append(res.hash.hexdigest())
                        logger.debug(f'Hash added to master list: {res.hash.hexdigest()}')
                        logger.info(f'Downloaded submission {submission.name}')
