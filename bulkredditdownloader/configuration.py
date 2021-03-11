#!/usr/bin/env python3
# coding=utf-8

from argparse import Namespace
from typing import Optional

import click


class Configuration(Namespace):
    def __init__(self):
        super(Configuration, self).__init__()
        self.directory: str = '.'
        self.limit: Optional[int] = None
        self.link: list[str] = []
        self.multireddit: list[str] = []
        self.no_dupes: bool = False
        self.saved: bool = False
        self.search: Optional[str] = None
        self.set_file_scheme: str = '{REDDITOR}_{TITLE}_{POSTID}'
        self.set_folder_scheme: str = '{SUBREDDIT}'
        self.skip: list[str] = []
        self.skip_domain: list[str] = []
        self.sort: str = 'hot'
        self.submitted: bool = False
        self.subreddit: list[str] = []
        self.time: str = 'all'
        self.upvoted: bool = False
        self.user: Optional[str] = None
        self.verbose: int = 0

    def process_click_arguments(self, context: click.Context):
        for arg_key in context.params.keys():
            if arg_key in vars(self) and context.params[arg_key] is not None:
                vars(self)[arg_key] = context.params[arg_key]
