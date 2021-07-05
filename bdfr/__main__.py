#!/usr/bin/env python3

import logging
import sys

import click

from bdfr.archiver import Archiver
from bdfr.cloner import RedditCloner
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader

logger = logging.getLogger()

_common_options = [
    click.argument('directory', type=str),
    click.option('--authenticate', is_flag=True, default=None),
    click.option('--config', type=str, default=None),
    click.option('--disable-module', multiple=True, default=None, type=str),
    click.option('--include-id-file', multiple=True, default=None),
    click.option('--log', type=str, default=None),
    click.option('--saved', is_flag=True, default=None),
    click.option('--search', default=None, type=str),
    click.option('--submitted', is_flag=True, default=None),
    click.option('--time-format', type=str, default=None),
    click.option('--upvoted', is_flag=True, default=None),
    click.option('-L', '--limit', default=None, type=int),
    click.option('-l', '--link', multiple=True, default=None, type=str),
    click.option('-m', '--multireddit', multiple=True, default=None, type=str),
    click.option('-S', '--sort', type=click.Choice(('hot', 'top', 'new', 'controversial', 'rising', 'relevance')),
                 default=None),
    click.option('-s', '--subreddit', multiple=True, default=None, type=str),
    click.option('-t', '--time', type=click.Choice(('all', 'hour', 'day', 'week', 'month', 'year')), default=None),
    click.option('-u', '--user', type=str, multiple=True, default=None),
    click.option('-v', '--verbose', default=None, count=True),
]

_downloader_options = [
    click.option('--file-scheme', default=None, type=str),
    click.option('--folder-scheme', default=None, type=str),
    click.option('--make-hard-links', is_flag=True, default=None),
    click.option('--max-wait-time', type=int, default=None),
    click.option('--no-dupes', is_flag=True, default=None),
    click.option('--search-existing', is_flag=True, default=None),
    click.option('--exclude-id', default=None, multiple=True),
    click.option('--exclude-id-file', default=None, multiple=True),
    click.option('--skip', default=None, multiple=True),
    click.option('--skip-domain', default=None, multiple=True),
    click.option('--skip-subreddit', default=None, multiple=True),
]

_archiver_options = [
    click.option('--all-comments', is_flag=True, default=None),
    click.option('--comment-context', is_flag=True, default=None),
    click.option('-f', '--format', type=click.Choice(('xml', 'json', 'yaml')), default=None),
]


def _add_options(opts: list):
    def wrap(func):
        for opt in opts:
            func = opt(func)
        return func
    return wrap


@click.group()
def cli():
    pass


@cli.command('download')
@_add_options(_common_options)
@_add_options(_downloader_options)
@click.pass_context
def cli_download(context: click.Context, **_):
    config = Configuration()
    config.process_click_arguments(context)
    setup_logging(config.verbose)
    try:
        reddit_downloader = RedditDownloader(config)
        reddit_downloader.download()
    except Exception:
        logger.exception('Downloader exited unexpectedly')
        raise
    else:
        logger.info('Program complete')


@cli.command('archive')
@_add_options(_common_options)
@_add_options(_archiver_options)
@click.pass_context
def cli_archive(context: click.Context, **_):
    config = Configuration()
    config.process_click_arguments(context)
    setup_logging(config.verbose)
    try:
        reddit_archiver = Archiver(config)
        reddit_archiver.download()
    except Exception:
        logger.exception('Archiver exited unexpectedly')
        raise
    else:
        logger.info('Program complete')


@cli.command('clone')
@_add_options(_common_options)
@_add_options(_archiver_options)
@_add_options(_downloader_options)
@click.pass_context
def cli_clone(context: click.Context, **_):
    config = Configuration()
    config.process_click_arguments(context)
    setup_logging(config.verbose)
    try:
        reddit_scraper = RedditCloner(config)
        reddit_scraper.download()
    except Exception:
        logger.exception('Scraper exited unexpectedly')
        raise
    else:
        logger.info('Program complete')


def setup_logging(verbosity: int):
    class StreamExceptionFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            result = not (record.levelno == logging.ERROR and record.exc_info)
            return result

    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    stream.addFilter(StreamExceptionFilter())

    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)

    logger.addHandler(stream)
    if verbosity <= 0:
        stream.setLevel(logging.INFO)
    elif verbosity == 1:
        stream.setLevel(logging.DEBUG)
    else:
        stream.setLevel(9)
    logging.getLogger('praw').setLevel(logging.CRITICAL)
    logging.getLogger('prawcore').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)


if __name__ == '__main__':
    cli()
