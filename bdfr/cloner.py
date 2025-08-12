#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from collections.abc import Iterable
from time import sleep

import prawcore

from bdfr.archiver import Archiver
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader

logger = logging.getLogger(__name__)


class RedditCloner(RedditDownloader, Archiver):
    def __init__(self, args: Configuration, logging_handlers: Iterable[logging.Handler] = ()):
        super(RedditCloner, self).__init__(args, logging_handlers)

    def download(self):
        for generator in self.reddit_lists:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            for retry in range(self.args.max_wait_retry or 1):
=======
            for retry in range(5):
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
            for retry in range(self.args.max_wait_retry or 1):
>>>>>>> b5cecfb (Resync)
=======
            for retry in range(5):
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
            for retry in range(self.args.max_wait_retry or 1):
>>>>>>> b5cecfb (Resync)
=======
            for retry in range(5):
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
            for retry in range(self.args.max_wait_retry or 1):
>>>>>>> b5cecfb (Resync)
                try:
                    for submission in generator:
                        try:
                            self._download_submission(submission)
                            self.write_entry(submission)
                        except prawcore.PrawcoreException as e:
                            logger.error(f"Submission {submission.id} failed to be cloned due to a PRAW exception: {e}")
                    break
                except prawcore.PrawcoreException as e:
                    logger.error(f"The submission after {submission.id} failed to download due to a PRAW exception: {e}")
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
                    logger.debug(f"Waiting {self.args.max_wait_time} seconds to continue")
                    sleep(self.args.max_wait_time)
=======
                    logger.debug("Waiting 60 seconds to continue")
                    sleep(60)
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
                    logger.debug(f"Waiting {self.args.max_wait_time} seconds to continue")
                    sleep(self.args.max_wait_time)
>>>>>>> b5cecfb (Resync)
=======
                    logger.debug("Waiting 60 seconds to continue")
                    sleep(60)
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
                    logger.debug(f"Waiting {self.args.max_wait_time} seconds to continue")
                    sleep(self.args.max_wait_time)
>>>>>>> b5cecfb (Resync)
=======
                    logger.debug("Waiting 60 seconds to continue")
                    sleep(60)
>>>>>>> d33a9b6 (Retry the current action 5x every 60s pause instead of skipping to the next)
=======
                    logger.debug(f"Waiting {self.args.max_wait_time} seconds to continue")
                    sleep(self.args.max_wait_time)
>>>>>>> b5cecfb (Resync)
