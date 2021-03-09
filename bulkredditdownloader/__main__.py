#!/usr/bin/env python3

import argparse
import logging
import sys

from bulkredditdownloader.downloader import RedditDownloader
from bulkredditdownloader.exceptions import BulkDownloaderException

logger = logging.getLogger()
parser = argparse.ArgumentParser(allow_abbrev=False,
                                 description='This program downloads media from reddit posts')


def _add_options():
    parser.add_argument('directory',
                        help='Specifies the directory where posts will be downloaded to',
                        metavar='DIRECTORY')
    parser.add_argument('--verbose', '-v',
                        action='count',
                        default=0,
                        )
    parser.add_argument('--link', '-l',
                        help='Get posts from link',
                        action='append',
                        default=[],
                        metavar='link')
    parser.add_argument('--submitted',
                        action='store_true',
                        help='Gets posts of --user')
    parser.add_argument('--saved',
                        action='store_true',
                        help='Gets upvoted posts of --user')
    parser.add_argument('--upvoted',
                        action='store_true',
                        help='Gets upvoted posts of --user')
    parser.add_argument('--subreddit',
                        nargs='+',
                        help='Triggers subreddit mode and takes subreddit name. use \"frontpage\" for frontpage',
                        metavar='SUBREDDIT',
                        type=str)
    parser.add_argument('--multireddit',
                        help='Triggers multireddit mode and takes multireddit name',
                        metavar='MULTIREDDIT',
                        action='append',
                        type=str)
    parser.add_argument('--authenticate',
                        action='store_true')
    parser.add_argument('--user',
                        help='reddit username if needed. use "me" for current user',
                        required='--multireddit' in sys.argv or '--submitted' in sys.argv,
                        metavar='redditor',
                        default=None,
                        type=str)
    parser.add_argument('--search',
                        help='Searches for given query in given subreddits',
                        metavar='query',
                        default=None,
                        type=str)
    parser.add_argument('--sort',
                        help='Either hot, top, new, controversial, rising or relevance default: hot',
                        choices=['hot', 'top', 'new', 'controversial', 'rising', 'relevance'],
                        metavar='SORT TYPE',
                        default='hot',
                        type=str)
    parser.add_argument('--limit',
                        help='default: unlimited',
                        metavar='Limit',
                        default=None,
                        type=int)
    parser.add_argument('--time',
                        help='Either hour, day, week, month, year or all. default: all',
                        choices=['all', 'hour', 'day', 'week', 'month', 'year'],
                        metavar='TIME_LIMIT',
                        default='all',
                        type=str)
    parser.add_argument('--skip',
                        nargs='+',
                        help='Skip posts with given type',
                        type=str,
                        default=[])
    parser.add_argument('--skip-domain',
                        nargs='+',
                        help='Skip posts with given domain',
                        type=str,
                        default=[])
    parser.add_argument('--set-folder-scheme',
                        action='store_true',
                        help='Set custom folderpath',
                        default='{SUBREDDIT}'
                        )
    parser.add_argument('--set-file-scheme',
                        action='store_true',
                        help='Set custom filename',
                        default='{REDDITOR}_{TITLE}_{POSTID}'
                        )
    parser.add_argument('--no-dupes',
                        action='store_true',
                        help='Do not download duplicate posts on different subreddits',
                        )


def _setup_logging(verbosity: int):
    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if verbosity < 0:
        stream.setLevel(logging.INFO)
    else:
        stream.setLevel(logging.DEBUG)

    logging.getLogger('praw').setLevel(logging.CRITICAL)
    logging.getLogger('prawcore').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)


def main(args: argparse.Namespace):
    _setup_logging(args.verbose)
    try:
        reddit_downloader = RedditDownloader(args)
        reddit_downloader.download()
    except BulkDownloaderException as e:
        logger.critical(f'An error occured {e}')


if __name__ == '__main__':
    _add_options()
    args = parser.parse_args()
    main(args)
