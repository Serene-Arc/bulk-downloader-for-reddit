#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

import click
import requests

from bdfr import __version__
from bdfr.archiver import Archiver
from bdfr.cloner import RedditCloner
from bdfr.completion import Completion
from bdfr.configuration import Configuration
from bdfr.downloader import RedditDownloader

logger = logging.getLogger()

_common_options = [
    click.argument("directory", type=str),
    click.option("--authenticate", is_flag=True, default=None),
    click.option("--config", type=str, default=None),
    click.option("--disable-module", multiple=True, default=None, type=str),
    click.option("--exclude-id", default=None, multiple=True),
    click.option("--exclude-id-file", default=None, multiple=True),
    click.option("--file-scheme", default=None, type=str),
    click.option("--filename-restriction-scheme", type=click.Choice(("linux", "windows")), default=None),
    click.option("--folder-scheme", default=None, type=str),
    click.option("--ignore-user", type=str, multiple=True, default=None),
    click.option("--include-id-file", multiple=True, default=None),
    click.option("--log", type=str, default=None),
    click.option("--opts", type=str, default=None),
    click.option("--saved", is_flag=True, default=None),
    click.option("--search", default=None, type=str),
    click.option("--submitted", is_flag=True, default=None),
    click.option("--subscribed", is_flag=True, default=None),
    click.option("--time-format", type=str, default=None),
    click.option("--upvoted", is_flag=True, default=None),
    click.option("-L", "--limit", default=None, type=int),
    click.option("-l", "--link", multiple=True, default=None, type=str),
    click.option("-m", "--multireddit", multiple=True, default=None, type=str),
    click.option(
        "-S", "--sort", type=click.Choice(("hot", "top", "new", "controversial", "rising", "relevance")), default=None
    ),
    click.option("-s", "--subreddit", multiple=True, default=None, type=str),
    click.option("-t", "--time", type=click.Choice(("all", "hour", "day", "week", "month", "year")), default=None),
    click.option("-u", "--user", type=str, multiple=True, default=None),
    click.option("-v", "--verbose", default=None, count=True),
]

_downloader_options = [
    click.option("--make-hard-links", is_flag=True, default=None),
    click.option("--max-wait-time", type=int, default=None),
    click.option("--no-dupes", is_flag=True, default=None),
    click.option("--search-existing", is_flag=True, default=None),
    click.option("--skip", default=None, multiple=True),
    click.option("--skip-domain", default=None, multiple=True),
    click.option("--skip-subreddit", default=None, multiple=True),
    click.option("--min-score", type=int, default=None),
    click.option("--max-score", type=int, default=None),
    click.option("--min-score-ratio", type=float, default=None),
    click.option("--max-score-ratio", type=float, default=None),
    click.option("--enable-downloads-db", is_flag=True, default=None),
    click.option("--downloads-db-name", type=str, default=None),
]

_archiver_options = [
    click.option("--all-comments", is_flag=True, default=None),
    click.option("--comment-context", is_flag=True, default=None),
    click.option("-f", "--format", type=click.Choice(("xml", "json", "yaml")), default=None),
]


def _add_options(opts: list):
    def wrap(func):
        for opt in opts:
            func = opt(func)
        return func

    return wrap


def _check_version(context, param, value):
    if not value or context.resilient_parsing:
        return
    current = __version__
    latest = requests.get("https://pypi.org/pypi/bdfr/json").json()["info"]["version"]
    print(f"You are currently using v{current} the latest is v{latest}")
    context.exit()


@click.group()
@click.help_option("-h", "--help")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_check_version,
    help="Check version and exit.",
)
def cli():
    """BDFR is used to download and archive content from Reddit."""
    pass


@cli.command("download")
@_add_options(_common_options)
@_add_options(_downloader_options)
@click.help_option("-h", "--help")
@click.pass_context
def cli_download(context: click.Context, **_):
    """Used to download content posted to Reddit."""
    config = Configuration()
    config.process_click_arguments(context)
    silence_module_loggers()
    stream = make_console_logging_handler(config.verbose)
    try:
        reddit_downloader = RedditDownloader(config, [stream])
        reddit_downloader.download()
    except Exception:
        logger.exception("Downloader exited unexpectedly")
        raise
    else:
        logger.info("Program complete")


@cli.command("archive")
@_add_options(_common_options)
@_add_options(_archiver_options)
@click.help_option("-h", "--help")
@click.pass_context
def cli_archive(context: click.Context, **_):
    """Used to archive post data from Reddit."""
    config = Configuration()
    config.process_click_arguments(context)
    silence_module_loggers()
    stream = make_console_logging_handler(config.verbose)
    try:
        reddit_archiver = Archiver(config, [stream])
        reddit_archiver.download()
    except Exception:
        logger.exception("Archiver exited unexpectedly")
        raise
    else:
        logger.info("Program complete")


@cli.command("clone")
@_add_options(_common_options)
@_add_options(_archiver_options)
@_add_options(_downloader_options)
@click.help_option("-h", "--help")
@click.pass_context
def cli_clone(context: click.Context, **_):
    """Combines archive and download commands."""
    config = Configuration()
    config.process_click_arguments(context)
    silence_module_loggers()
    stream = make_console_logging_handler(config.verbose)
    try:
        reddit_scraper = RedditCloner(config, [stream])
        reddit_scraper.download()
    except Exception:
        logger.exception("Scraper exited unexpectedly")
        raise
    else:
        logger.info("Program complete")


@cli.command("completion")
@click.argument("shell", type=click.Choice(("all", "bash", "fish", "zsh"), case_sensitive=False), default="all")
@click.help_option("-h", "--help")
@click.option("-u", "--uninstall", is_flag=True, default=False, help="Uninstall completion")
def cli_completion(shell: str, uninstall: bool):
    """\b
    Installs shell completions for BDFR.
    Options: all, bash, fish, zsh
    Default: all"""
    shell = shell.lower()
    if sys.platform == "win32":
        print("Completions are not currently supported on Windows.")
        return
    if uninstall and click.confirm(f"Would you like to uninstall {shell} completions for BDFR"):
        Completion(shell).uninstall()
        return
    if shell not in ("all", "bash", "fish", "zsh"):
        print(f"{shell} is not a valid option.")
        print("Options: all, bash, fish, zsh")
        return
    if click.confirm(f"Would you like to install {shell} completions for BDFR"):
        Completion(shell).install()


def make_console_logging_handler(verbosity: int) -> logging.StreamHandler:
    class StreamExceptionFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            result = not (record.levelno == logging.ERROR and record.exc_info)
            return result

    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    stream.addFilter(StreamExceptionFilter())

    formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] - %(message)s")
    stream.setFormatter(formatter)

    if verbosity <= 0:
        stream.setLevel(logging.INFO)
    elif verbosity == 1:
        stream.setLevel(logging.DEBUG)
    else:
        stream.setLevel(9)
    return stream


def silence_module_loggers():
    logging.getLogger("praw").setLevel(logging.CRITICAL)
    logging.getLogger("prawcore").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


if __name__ == "__main__":
    cli()
