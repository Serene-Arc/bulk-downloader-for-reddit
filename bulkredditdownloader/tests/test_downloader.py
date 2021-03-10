#!/usr/bin/env python3
# coding=utf-8

import argparse
import re
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock

import praw
import praw.models
import pytest

from bulkredditdownloader.__main__ import _setup_logging
from bulkredditdownloader.download_filter import DownloadFilter
from bulkredditdownloader.downloader import RedditDownloader, RedditTypes
from bulkredditdownloader.exceptions import BulkDownloaderException, RedditAuthenticationError, RedditUserError
from bulkredditdownloader.file_name_formatter import FileNameFormatter
from bulkredditdownloader.site_authenticator import SiteAuthenticator


@pytest.fixture()
def args() -> argparse.Namespace:
    args = argparse.Namespace()

    args.directory = '.'
    args.verbose = 0
    args.link = []
    args.submitted = False
    args.upvoted = False
    args.saved = False
    args.subreddit = []
    args.multireddit = []
    args.user = None
    args.search = None
    args.sort = 'hot'
    args.limit = None
    args.time = 'all'
    args.skip = []
    args.skip_domain = []
    args.set_folder_scheme = '{SUBREDDIT}'
    args.set_file_scheme = '{REDDITOR}_{TITLE}_{POSTID}'
    args.no_dupes = False

    return args


@pytest.fixture()
def downloader_mock(args: argparse.Namespace):
    mock_downloader = MagicMock()
    mock_downloader.args = args
    return mock_downloader


def assert_all_results_are_submissions(result_limit: int, results: list[Iterator]):
    results = [sub for res in results for sub in res]
    assert all([isinstance(res, praw.models.Submission) for res in results])
    if result_limit is not None:
        assert len(results) == result_limit
    return results


def test_determine_directories(tmp_path: Path, downloader_mock: MagicMock):
    downloader_mock.args.directory = tmp_path / 'test'
    RedditDownloader._determine_directories(downloader_mock)

    assert Path(tmp_path / 'test').exists()
    assert downloader_mock.logfile_directory == Path(tmp_path / 'test' / 'LOG_FILES')
    assert downloader_mock.logfile_directory.exists()


@pytest.mark.parametrize(('skip_extensions', 'skip_domains'), (
    ([], []),
    (['.test'], ['test.com']),
))
def test_create_download_filter(skip_extensions: list[str], skip_domains: list[str], downloader_mock: MagicMock):
    downloader_mock.args.skip = skip_extensions
    downloader_mock.args.skip_domain = skip_domains
    result = RedditDownloader._create_download_filter(downloader_mock)

    assert isinstance(result, DownloadFilter)
    assert result.excluded_domains == skip_domains
    assert result.excluded_extensions == skip_extensions


@pytest.mark.parametrize(('test_time', 'expected'), (
    ('all', 'all'),
    ('hour', 'hour'),
    ('day', 'day'),
    ('week', 'week'),
    ('random', 'all'),
    ('', 'all'),
))
def test_create_time_filter(test_time: str, expected: str, downloader_mock: MagicMock):
    downloader_mock.args.time = test_time
    result = RedditDownloader._create_time_filter(downloader_mock)

    assert isinstance(result, RedditTypes.TimeType)
    assert result.name.lower() == expected


@pytest.mark.parametrize(('test_sort', 'expected'), (
    ('', 'hot'),
    ('hot', 'hot'),
    ('controversial', 'controversial'),
    ('new', 'new'),
))
def test_create_sort_filter(test_sort: str, expected: str, downloader_mock: MagicMock):
    downloader_mock.args.sort = test_sort
    result = RedditDownloader._create_sort_filter(downloader_mock)

    assert isinstance(result, RedditTypes.SortType)
    assert result.name.lower() == expected


@pytest.mark.parametrize(('test_file_scheme', 'test_folder_scheme'), (
    ('{POSTID}', '{SUBREDDIT}'),
    ('{REDDITOR}_{TITLE}_{POSTID}', '{SUBREDDIT}'),
    ('{POSTID}', 'test'),
    ('{POSTID}', ''),
))
def test_create_file_name_formatter(test_file_scheme: str, test_folder_scheme: str, downloader_mock: MagicMock):
    downloader_mock.args.set_file_scheme = test_file_scheme
    downloader_mock.args.set_folder_scheme = test_folder_scheme
    result = RedditDownloader._create_file_name_formatter(downloader_mock)

    assert isinstance(result, FileNameFormatter)
    assert result.file_format_string == test_file_scheme
    assert result.directory_format_string == test_folder_scheme


@pytest.mark.parametrize(('test_file_scheme', 'test_folder_scheme'), (
    ('', ''),
    ('', '{SUBREDDIT}'),
    ('test', '{SUBREDDIT}'),
))
def test_create_file_name_formatter_bad(test_file_scheme: str, test_folder_scheme: str, downloader_mock: MagicMock):
    downloader_mock.args.set_file_scheme = test_file_scheme
    downloader_mock.args.set_folder_scheme = test_folder_scheme
    with pytest.raises(BulkDownloaderException):
        RedditDownloader._create_file_name_formatter(downloader_mock)


def test_create_authenticator(downloader_mock: MagicMock):
    result = RedditDownloader._create_authenticator(downloader_mock)
    assert isinstance(result, SiteAuthenticator)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_submission_ids', (
    ('lvpf4l',),
    ('lvpf4l', 'lvqnsn'),
    ('lvpf4l', 'lvqnsn', 'lvl9kd'),
))
def test_get_submissions_from_link(
        test_submission_ids: list[str],
        reddit_instance: praw.Reddit,
        downloader_mock: MagicMock):
    downloader_mock.args.link = test_submission_ids
    downloader_mock.reddit_instance = reddit_instance
    results = RedditDownloader._get_submissions_from_link(downloader_mock)
    assert all([isinstance(sub, praw.models.Submission) for res in results for sub in res])
    assert len(results[0]) == len(test_submission_ids)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_subreddits', 'limit'), (
    (('Futurology',), 10),
    (('Futurology',), 20),
    (('Futurology', 'Python'), 10),
    (('Futurology',), 100),
    (('Futurology',), 0),
))
def test_get_subreddit_normal(
        test_subreddits: list[str],
        limit: int,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.args.limit = limit
    downloader_mock.args.subreddit = test_subreddits
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    results = RedditDownloader._get_subreddits(downloader_mock)
    results = assert_all_results_are_submissions(
        (limit * len(test_subreddits)) if limit else None, results)
    assert all([res.subreddit.display_name in test_subreddits for res in results])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_subreddits', 'search_term', 'limit'), (
    (('Python',), 'scraper', 10),
    (('Python',), '', 10),
    (('Python',), 'djsdsgewef', 0),
))
def test_get_subreddit_search(
        test_subreddits: list[str],
        search_term: str,
        limit: int,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.args.limit = limit
    downloader_mock.args.search = search_term
    downloader_mock.args.subreddit = test_subreddits
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    results = RedditDownloader._get_subreddits(downloader_mock)
    results = assert_all_results_are_submissions(
        (limit * len(test_subreddits)) if limit else None, results)
    assert all([res.subreddit.display_name in test_subreddits for res in results])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_user', 'test_multireddits', 'limit'), (
    ('helen_darten', ('cuteanimalpics',), 10),
    ('korfor', ('chess',), 100),
))
# Good sources at https://www.reddit.com/r/multihub/
def test_get_multireddits_public(
        test_user: str,
        test_multireddits: list[str],
        limit: int,
        reddit_instance: praw.Reddit,
        downloader_mock: MagicMock):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    downloader_mock.args.limit = limit
    downloader_mock.args.multireddit = test_multireddits
    downloader_mock.args.user = test_user
    downloader_mock.reddit_instance = reddit_instance
    results = RedditDownloader._get_multireddits(downloader_mock)
    assert_all_results_are_submissions((limit * len(test_multireddits)) if limit else None, results)


@pytest.mark.online
@pytest.mark.reddit
def test_get_multireddits_no_user(downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.args.multireddit = ['test']
    with pytest.raises(BulkDownloaderException):
        RedditDownloader._get_multireddits(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
def test_get_multireddits_not_authenticated(downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.args.multireddit = ['test']
    downloader_mock.authenticated = False
    downloader_mock.reddit_instance = reddit_instance
    with pytest.raises(RedditAuthenticationError):
        RedditDownloader._get_multireddits(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_user', 'limit'), (
    ('danigirl3694', 10),
    ('danigirl3694', 50),
    ('CapitanHam', None),
))
def test_get_user_submissions(test_user: str, limit: int, downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.args.limit = limit
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    downloader_mock.args.submitted = True
    downloader_mock.args.user = test_user
    downloader_mock.authenticated = False
    downloader_mock.reddit_instance = reddit_instance
    results = RedditDownloader._get_user_data(downloader_mock)
    results = assert_all_results_are_submissions(limit, results)
    assert all([res.author.name == test_user for res in results])


@pytest.mark.online
@pytest.mark.reddit
def test_get_user_no_user(downloader_mock: MagicMock):
    downloader_mock.args.upvoted = True
    with pytest.raises(BulkDownloaderException):
        RedditDownloader._get_user_data(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_user', (
    'rockcanopicjartheme',
    'exceptionalcatfishracecarbatter',
))
def test_get_user_nonexistent_user(test_user: str, downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.args.user = test_user
    downloader_mock.args.upvoted = True
    downloader_mock._check_user_existence.return_value = RedditDownloader._check_user_existence(
        downloader_mock, test_user)
    with pytest.raises(RedditUserError):
        RedditDownloader._get_user_data(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
def test_get_user_upvoted(downloader_mock: MagicMock, authenticated_reddit_instance: praw.Reddit):
    downloader_mock.reddit_instance = authenticated_reddit_instance
    downloader_mock.args.user = 'me'
    downloader_mock.args.upvoted = True
    downloader_mock.args.limit = 10
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    RedditDownloader._resolve_user_name(downloader_mock)
    results = RedditDownloader._get_user_data(downloader_mock)
    assert_all_results_are_submissions(10, results)


@pytest.mark.online
@pytest.mark.reddit
def test_get_user_upvoted_unauthenticated(downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.args.user = 'random'
    downloader_mock.args.upvoted = True
    downloader_mock.authenticated = False
    with pytest.raises(RedditAuthenticationError):
        RedditDownloader._get_user_data(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
def test_get_user_saved(downloader_mock: MagicMock, authenticated_reddit_instance: praw.Reddit):
    downloader_mock.reddit_instance = authenticated_reddit_instance
    downloader_mock.args.user = 'me'
    downloader_mock.args.saved = True
    downloader_mock.args.limit = 10
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    RedditDownloader._resolve_user_name(downloader_mock)
    results = RedditDownloader._get_user_data(downloader_mock)
    assert_all_results_are_submissions(10, results)


@pytest.mark.online
@pytest.mark.reddit
def test_get_user_saved_unauthenticated(downloader_mock: MagicMock, reddit_instance: praw.Reddit):
    downloader_mock.args.user = 'random'
    downloader_mock.args.saved = True
    downloader_mock.authenticated = False
    with pytest.raises(RedditAuthenticationError):
        RedditDownloader._get_user_data(downloader_mock)


@pytest.mark.online
@pytest.mark.reddit
def test_download_submission(downloader_mock: MagicMock, reddit_instance: praw.Reddit, tmp_path: Path):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.set_folder_scheme = ''
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    downloader_mock.master_hash_list = []
    submission = downloader_mock.reddit_instance.submission(id='ljyy27')
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    assert len(folder_contents) == 4


@pytest.mark.online
@pytest.mark.reddit
def test_download_submission_file_exists(
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
        tmp_path: Path,
        capsys: pytest.CaptureFixture):
    _setup_logging(3)
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.set_folder_scheme = ''
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    downloader_mock.master_hash_list = []
    submission = downloader_mock.reddit_instance.submission(id='m1hqw6')
    Path(tmp_path, 'Arneeman_Metagaming isn\'t always a bad thing_m1hqw6_1.png').touch()
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert len(folder_contents) == 1
    assert 'File already exists: ' in output.out


@pytest.mark.online
@pytest.mark.reddit
def test_download_submission_hash_exists(
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
        tmp_path: Path,
        capsys: pytest.CaptureFixture):
    _setup_logging(3)
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.set_folder_scheme = ''
    downloader_mock.args.no_dupes = True
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    downloader_mock.master_hash_list = ['a912af8905ae468e0121e9940f797ad7']
    submission = downloader_mock.reddit_instance.submission(id='m1hqw6')
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert len(folder_contents) == 0
    assert re.search(r'Resource from .*? downloaded elsewhere', output.out)
