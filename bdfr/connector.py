#!/usr/bin/env python3

import configparser
import importlib.resources
import itertools
import logging
import logging.handlers
import platform
import re
import shutil
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from time import sleep
from typing import Union

import appdirs
import praw
import praw.exceptions
import praw.models
import prawcore

from bdfr import __version__
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
        ALL = "all"
        DAY = "day"
        HOUR = "hour"
        MONTH = "month"
        WEEK = "week"
        YEAR = "year"


class RedditConnector(metaclass=ABCMeta):
    def __init__(self, args: Configuration, logging_handlers: Iterable[logging.Handler] = ()) -> None:
        self.args = args
        self.config_directories = appdirs.AppDirs("bdfr", "BDFR")
        self.determine_directories()
        self.load_config()
        self.read_config()
        file_log = self.create_file_logger()
        self._apply_logging_handlers(itertools.chain(logging_handlers, [file_log]))
        self.run_time = datetime.now().isoformat()
        self._setup_internal_objects()

        self.reddit_lists = self.retrieve_reddit_lists()

    def _setup_internal_objects(self) -> None:
        self.parse_disabled_modules()

        self.download_filter = self.create_download_filter()
        logger.log(9, "Created download filter")
        self.time_filter = self.create_time_filter()
        logger.log(9, "Created time filter")
        self.sort_filter = self.create_sort_filter()
        logger.log(9, "Created sort filter")
        self.file_name_formatter = self.create_file_name_formatter()
        logger.log(9, "Create file name formatter")

        self.user_agent = praw.const.USER_AGENT_FORMAT.format(":".join([platform.uname()[0], __package__, __version__]))
        self.create_reddit_instance()
        self.args.user = list(filter(None, [self.resolve_user_name(user) for user in self.args.user]))

        self.excluded_submission_ids = set.union(
            self.read_id_files(self.args.exclude_id_file),
            set(self.args.exclude_id),
        )

        self.args.link = list(itertools.chain(self.args.link, self.read_id_files(self.args.include_id_file)))

        self.master_hash_list = {}
        self.authenticator = self.create_authenticator()
        logger.log(9, "Created site authenticator")

        self.args.skip_subreddit = self.split_args_input(self.args.skip_subreddit)
        self.args.skip_subreddit = {sub.lower() for sub in self.args.skip_subreddit}

    @staticmethod
    def _apply_logging_handlers(handlers: Iterable[logging.Handler]) -> None:
        main_logger = logging.getLogger()
        for handler in handlers:
            main_logger.addHandler(handler)

    def read_config(self) -> None:
        """Read any cfg values that need to be processed"""
        if self.args.max_wait_time is None:
            self.args.max_wait_time = self.cfg_parser.getint("DEFAULT", "max_wait_time", fallback=120)
            logger.debug(f"Setting maximum download wait time to {self.args.max_wait_time} seconds")
        if self.args.time_format is None:
            option = self.cfg_parser.get("DEFAULT", "time_format", fallback="ISO")
            if re.match(r"^[\s\'\"]*$", option):
                option = "ISO"
            logger.debug(f"Setting datetime format string to {option}")
            self.args.time_format = option
        if not self.args.disable_module:
            self.args.disable_module = [self.cfg_parser.get("DEFAULT", "disabled_modules", fallback="")]
        if not self.args.filename_restriction_scheme:
            self.args.filename_restriction_scheme = self.cfg_parser.get(
                "DEFAULT", "filename_restriction_scheme", fallback=None
            )
            logger.debug(f"Setting filename restriction scheme to {self.args.filename_restriction_scheme!r}")
        # Update config on disk
        with Path(self.config_location).open(mode="w") as file:
            self.cfg_parser.write(file)

    def parse_disabled_modules(self) -> None:
        disabled_modules = self.args.disable_module
        disabled_modules = self.split_args_input(disabled_modules)
        disabled_modules = {name.strip().lower() for name in disabled_modules}
        self.args.disable_module = disabled_modules
        logger.debug(f"Disabling the following modules: {', '.join(self.args.disable_module)}")

    def create_reddit_instance(self) -> None:
        if self.args.authenticate:
            logger.debug("Using authenticated Reddit instance")
            client_id = self.cfg_parser.get("DEFAULT", "client_id")
            client_secret = self.cfg_parser.get("DEFAULT", "client_secret", fallback=None)
            if client_id == "U-6gk4ZCh3IeNQ":
                logger.warning(
                    "You are using the default app ID for the BDFR; this will result in you sharing a request quota"
                    " with every other user. It is recommended to create your own app and put the ID and secret"
                    " in the configuration file"
                )
            if client_secret and client_secret.lower() == "none":
                client_secret = None
            if not self.cfg_parser.has_option("DEFAULT", "user_token"):
                logger.log(9, "Commencing OAuth2 authentication")
                scopes = self.cfg_parser.get("DEFAULT", "scopes", fallback="identity, history, read, save")
                scopes = OAuth2Authenticator.split_scopes(scopes)
                oauth2_authenticator = OAuth2Authenticator(
                    wanted_scopes=scopes,
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=self.user_agent,
                )
                token = oauth2_authenticator.retrieve_new_token()
                self.cfg_parser["DEFAULT"]["user_token"] = token
                with Path(self.config_location).open(mode="w") as file:
                    self.cfg_parser.write(file, True)
            token_manager = OAuth2TokenManager(self.cfg_parser, self.config_location)

            self.authenticated = True
            self.reddit_instance = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=self.user_agent,
                token_manager=token_manager,
                ratelimit_seconds=120,
            )
        else:
            logger.debug("Using unauthenticated Reddit instance")
            logger.warning(
                "Using an unauthenticated app like this will result in Reddit limiting queries to 10 requests a minute"
            )
            self.authenticated = False
            client_secret = self.cfg_parser.get("DEFAULT", "client_secret", fallback=None)
            if client_secret and client_secret.lower() == "none":
                client_secret = None
            self.reddit_instance = praw.Reddit(
                client_id=self.cfg_parser.get("DEFAULT", "client_id"),
                client_secret=client_secret,
                user_agent=self.user_agent,
                ratelimit_seconds=120,
            )

    def retrieve_reddit_lists(self) -> list[praw.models.ListingGenerator]:
        master_list = []
        master_list.extend(self.get_subreddits())
        logger.log(9, "Retrieved subreddits")
        master_list.extend(self.get_multireddits())
        logger.log(9, "Retrieved multireddits")
        master_list.extend(self.get_user_data())
        logger.log(9, "Retrieved user data")
        master_list.extend(self.get_submissions_from_link())
        logger.log(9, "Retrieved submissions for given links")
        return master_list

    def determine_directories(self) -> None:
        self.download_directory = Path(self.args.directory).resolve().expanduser()
        self.config_directory = Path(self.config_directories.user_config_dir)

        self.download_directory.mkdir(exist_ok=True, parents=True)
        self.config_directory.mkdir(exist_ok=True, parents=True)

    def load_config(self) -> None:
        self.cfg_parser = configparser.ConfigParser()
        if self.args.config:
            if (cfg_path := Path(self.args.config)).exists():
                self.cfg_parser.read(cfg_path)
                self.config_location = cfg_path
                return
        possible_paths = [
            Path("./config.cfg"),
            Path("./default_config.cfg"),
            Path(self.config_directory, "config.cfg"),
            Path(self.config_directory, "default_config.cfg"),
        ]
        self.config_location = None
        for path in possible_paths:
            if path.resolve().expanduser().exists():
                self.config_location = path
                logger.debug(f"Loading configuration from {path}")
                break
        if not self.config_location:
            with importlib.resources.path("bdfr", "default_config.cfg") as path:
                self.config_location = path
                shutil.copy(self.config_location, Path(self.config_directory, "default_config.cfg"))
        if not self.config_location:
            raise errors.BulkDownloaderException("Could not find a configuration file to load")
        self.cfg_parser.read(self.config_location)

    def create_file_logger(self) -> logging.handlers.RotatingFileHandler:
        if self.args.log is None:
            log_path = Path(self.config_directory, "log_output.txt")
        else:
            log_path = Path(self.args.log).resolve().expanduser()
            if not log_path.parent.exists():
                raise errors.BulkDownloaderException("Designated location for logfile does not exist")
        backup_count = self.cfg_parser.getint("DEFAULT", "backup_log_count", fallback=3)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            mode="a",
            backupCount=backup_count,
        )
        if log_path.exists():
            try:
                file_handler.doRollover()
            except PermissionError:
                logger.critical(
                    "Cannot rollover logfile, make sure this is the only "
                    "BDFR process or specify alternate logfile location"
                )
                raise
        formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] - %(message)s")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(0)
        return file_handler

    @staticmethod
    def sanitise_subreddit_name(subreddit: str) -> str:
        pattern = re.compile(r"^(?:https://www\.reddit\.com/)?(?:r/)?(.*?)/?$")
        match = re.match(pattern, subreddit)
        if not match:
            raise errors.BulkDownloaderException(f"Could not find subreddit name in string {subreddit!r}")
        return match.group(1)

    @staticmethod
    def split_args_input(entries: list[str]) -> set[str]:
        all_entries = []
        split_pattern = re.compile(r"[,;]\s?")
        for entry in entries:
            results = re.split(split_pattern, entry)
            all_entries.extend([RedditConnector.sanitise_subreddit_name(name) for name in results])
        return set(all_entries)

    def get_subreddits(self) -> list[praw.models.ListingGenerator]:
        out = []
        subscribed_subreddits = set()
        if self.args.subscribed:
            if self.args.authenticate:
                try:
                    subscribed_subreddits = list(self.reddit_instance.user.subreddits(limit=None))
                    subscribed_subreddits = {s.display_name for s in subscribed_subreddits}
                except prawcore.InsufficientScope:
                    logger.error("BDFR has insufficient scope to access subreddit lists")
            else:
                logger.error("Cannot find subscribed subreddits without an authenticated instance")
        if self.args.subreddit or subscribed_subreddits:
            for reddit in self.split_args_input(self.args.subreddit) | subscribed_subreddits:
                if reddit == "friends" and self.authenticated is False:
                    logger.error("Cannot read friends subreddit without an authenticated instance")
                    continue
                try:
                    reddit = self.reddit_instance.subreddit(reddit)
                    try:
                        self.check_subreddit_status(reddit)
                    except errors.BulkDownloaderException as e:
                        logger.error(e)
                        continue
                    if self.args.search:
                        out.append(
                            reddit.search(
                                self.args.search,
                                sort=self.sort_filter.name.lower(),
                                limit=self.args.limit,
                                time_filter=self.time_filter.value,
                            )
                        )
                        logger.debug(
                            f"Added submissions from subreddit {reddit} with the search term {self.args.search!r}"
                        )
                    else:
                        out.append(self.create_filtered_listing_generator(reddit))
                        logger.debug(f"Added submissions from subreddit {reddit}")
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException) as e:
                    logger.error(f"Failed to get submissions for subreddit {reddit}: {e}")
        return out

    def resolve_user_name(self, in_name: str) -> str:
        if in_name == "me":
            if self.authenticated:
                resolved_name = self.reddit_instance.user.me().name
                logger.log(9, f"Resolved user to {resolved_name}")
                return resolved_name
            else:
                logger.warning("To use 'me' as a user, an authenticated Reddit instance must be used")
        else:
            return in_name

    def get_submissions_from_link(self) -> list[list[praw.models.Submission]]:
        supplied_submissions = []
        for sub_id in self.args.link:
            if len(sub_id) in (6, 7):
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
                logger.error("Only 1 user can be supplied when retrieving from multireddits")
                return []
            out = []
            for multi in self.split_args_input(self.args.multireddit):
                try:
                    multi = self.reddit_instance.multireddit(redditor=self.args.user[0], name=multi)
                    if not multi.subreddits:
                        raise errors.BulkDownloaderException
                    out.append(self.create_filtered_listing_generator(multi))
                    logger.debug(f"Added submissions from multireddit {multi}")
                except (errors.BulkDownloaderException, praw.exceptions.PRAWException, prawcore.PrawcoreException) as e:
                    logger.error(f"Failed to get submissions for multireddit {multi}: {e}")
            return out
        else:
            return []

    def create_filtered_listing_generator(
        self, reddit_source: Union[praw.models.Subreddit, praw.models.Multireddit, praw.models.Redditor.submissions]
    ) -> Iterator:
        sort_function = self.determine_sort_function()
        if self.sort_filter in (RedditTypes.SortType.TOP, RedditTypes.SortType.CONTROVERSIAL):
            return sort_function(reddit_source, limit=self.args.limit, time_filter=self.time_filter.value)
        else:
            return sort_function(reddit_source, limit=self.args.limit)

    def get_user_data(self) -> list[Iterator]:
        if any([self.args.downvoted, self.args.saved, self.args.submitted, self.args.upvoted]):
            if not self.args.user:
                logger.warning("At least one user must be supplied to download user data")
                return []
            generators = []
            for user in self.args.user:
                try:
                    try:
                        self.check_user_existence(user)
                    except errors.BulkDownloaderException as e:
                        logger.error(e)
                        continue
                    if self.args.submitted:
                        logger.debug(f"Retrieving submitted posts of user {user}")
                        generators.append(
                            self.create_filtered_listing_generator(
                                self.reddit_instance.redditor(user).submissions,
                            )
                        )
                    if not self.authenticated and any((self.args.downvoted, self.args.saved, self.args.upvoted)):
                        logger.warning("Accessing user lists requires authentication")
                    else:
                        if self.args.upvoted:
                            logger.debug(f"Retrieving upvoted posts of user {user}")
                            generators.append(self.reddit_instance.redditor(user).upvoted(limit=self.args.limit))
                        if self.args.saved:
                            logger.debug(f"Retrieving saved posts of user {user}")
                            generators.append(self.reddit_instance.redditor(user).saved(limit=self.args.limit))
                        if self.args.downvoted:
                            logger.debug(f"Retrieving downvoted posts of user {user}")
                            generators.append(self.reddit_instance.redditor(user).downvoted(limit=self.args.limit))
                except prawcore.PrawcoreException as e:
                    logger.error(f"User {user} failed to be retrieved due to a PRAW exception: {e}")
                    logger.debug("Waiting 60 seconds to continue")
                    sleep(60)
            return generators
        else:
            return []

    def check_user_existence(self, name: str) -> None:
        user = self.reddit_instance.redditor(name=name)
        try:
            if user.id:
                return
        except prawcore.exceptions.NotFound:
            raise errors.BulkDownloaderException(f"Could not find user {name}")
        except AttributeError:
            if hasattr(user, "is_suspended"):
                raise errors.BulkDownloaderException(f"User {name} is banned")

    def create_file_name_formatter(self) -> FileNameFormatter:
        return FileNameFormatter(
            self.args.file_scheme, self.args.folder_scheme, self.args.time_format, self.args.filename_restriction_scheme
        )

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
    def download(self) -> None:
        pass

    @staticmethod
    def check_subreddit_status(subreddit: praw.models.Subreddit) -> None:
        if subreddit.display_name in ("all", "friends"):
            return
        try:
            if subreddit.id:
                return
        except prawcore.NotFound:
            raise errors.BulkDownloaderException(f"Source {subreddit.display_name} cannot be found")
        except prawcore.Redirect:
            raise errors.BulkDownloaderException(f"Source {subreddit.display_name} does not exist")
        except prawcore.Forbidden:
            raise errors.BulkDownloaderException(f"Source {subreddit.display_name} is private and cannot be scraped")

    @staticmethod
    def read_id_files(file_locations: list[str]) -> set[str]:
        out = []
        for id_file in file_locations:
            id_file = Path(id_file).resolve().expanduser()
            if not id_file.exists():
                logger.warning(f"ID file at {id_file} does not exist")
                continue
            with id_file.open("r") as file:
                for line in file:
                    out.append(line.strip())
        return set(out)
