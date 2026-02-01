#!/usr/bin/env python3

import logging
from collections.abc import Iterable
from time import sleep

import prawcore

from bdfr.archiver import Archiver
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader

logger = logging.getLogger(__name__)


class RedditCloner(RedditDownloader, Archiver):
    def __init__(self, args: Configuration, logging_handlers: Iterable[logging.Handler] = ()) -> None:
        super().__init__(args, logging_handlers)

    def download(self) -> None:
        for generator in self.reddit_lists:
            try:
                for submission in generator:
                    try:
                        self._download_submission(submission)
                        self.write_entry(submission)
                    except prawcore.PrawcoreException as e:
                        logger.error(f"Submission {submission.id} failed to be cloned due to a PRAW exception: {e}")
            except prawcore.PrawcoreException as e:
                logger.error(f"The submission after {submission.id} failed to download due to a PRAW exception: {e}")
                logger.debug("Waiting 60 seconds to continue")
                sleep(60)
