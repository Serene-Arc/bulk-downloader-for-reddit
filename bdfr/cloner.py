#!/usr/bin/env python3

import logging
from collections.abc import Iterable
from time import sleep

import prawcore

from bdfr.archiver import Archiver
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader
from bdfr.progress_bar import Progress

logger = logging.getLogger(__name__)


class RedditCloner(RedditDownloader, Archiver):
    def __init__(self, args: Configuration, logging_handlers: Iterable[logging.Handler] = ()) -> None:
        super().__init__(args, logging_handlers)

    def download(self) -> None:
        progress = Progress(self.args.progress_bar, len(self.reddit_lists))
        for generator in self.reddit_lists:
            progress.subreddit_new(generator)
            try:
                for submission in generator:
                    try:
                        success = self._download_submission(submission)
                        self.write_entry(submission)
                    except prawcore.PrawcoreException as e:
                        logger.error(f"Submission {submission.id} failed to be cloned due to a PRAW exception: {e}")
                        success = False
                    progress.post_done(submission, success)
            except prawcore.PrawcoreException as e:
                logger.error(f"The submission after {submission.id} failed to download due to a PRAW exception: {e}")
                logger.debug("Waiting 60 seconds to continue")
                sleep(60)
            progress.subreddit_done()
