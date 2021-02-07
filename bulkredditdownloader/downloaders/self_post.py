#!/usr/bin/env python3

import io
import logging
import pathlib
from pathlib import Path

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.errors import FileAlreadyExistsError, TypeInSkip
from bulkredditdownloader.utils import GLOBAL

logger = logging.getLogger(__name__)


class SelfPost(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.download()

    def download(self):
        if "self" in GLOBAL.arguments.skip:
            raise TypeInSkip

        self.directory.mkdir(exist_ok=True)
        filename = GLOBAL.config['filename'].format(**self.post)

        file_dir = self.directory / (filename + ".md")
        logger.info(file_dir)
        logger.info(filename + ".md")

        if Path.is_file(file_dir):
            raise FileAlreadyExistsError

        try:
            self._write_to_file(file_dir, self.post)
        except FileNotFoundError:
            file_dir = self.post['POSTID'] + ".md"
            file_dir = self.directory / file_dir

            self._write_to_file(file_dir, self.post)

    @staticmethod
    def _write_to_file(directory: pathlib.Path, post: dict):
        """Self posts are formatted here"""
        content = ("## ["
                   + post["TITLE"]
                   + "]("
                   + post["CONTENTURL"]
                   + ")\n"
                   + post["CONTENT"]
                   + "\n\n---\n\n"
                   + "submitted to [r/"
                   + post["SUBREDDIT"]
                   + "](https://www.reddit.com/r/"
                   + post["SUBREDDIT"]
                   + ") by [u/"
                   + post["REDDITOR"]
                   + "](https://www.reddit.com/user/"
                   + post["REDDITOR"]
                   + ")")

        with io.open(directory, "w", encoding="utf-8") as FILE:
            print(content, file=FILE)
        logger.info("Downloaded")
