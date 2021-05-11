#!/usr/bin/env python3
# coding=utf-8

import re
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock

import praw
import praw.models
import pytest

from bdfr.__main__ import setup_logging
from bdfr.configuration import Configuration
from bdfr.download_filter import DownloadFilter
from bdfr.downloader import RedditDownloader, RedditTypes
from bdfr.exceptions import BulkDownloaderException
from bdfr.file_name_formatter import FileNameFormatter
from bdfr.site_authenticator import SiteAuthenticator


@pytest.fixture()
def args() -> Configuration:
    args = Configuration()
    args.time_format = 'ISO'
    return args


@pytest.fixture()
def downloader_mock(args: Configuration):
    downloader_mock = MagicMock()
    downloader_mock.args = args
    downloader_mock._sanitise_subreddit_name = RedditDownloader._sanitise_subreddit_name
    downloader_mock._split_args_input = RedditDownloader._split_args_input
    downloader_mock.master_hash_list = {}
    return downloader_mock


def assert_all_results_are_submissions(result_limit: int, results: list[Iterator]):
    results = [sub for res in results for sub in res]
    assert all([isinstance(res, praw.models.Submission) for res in results])
    if result_limit is not None:
        assert len(results) == result_limit
    return results


def test_determine_directories(tmp_path: Path, downloader_mock: MagicMock):
    downloader_mock.args.directory = tmp_path / 'test'
    downloader_mock.config_directories.user_config_dir = tmp_path
    RedditDownloader._determine_directories(downloader_mock)
    assert Path(tmp_path / 'test').exists()


@pytest.mark.parametrize(('skip_extensions', 'skip_domains'), (
    ([], []),
    (['.test'], ['test.com'],),
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
    ('{POSTID}', '{SUBREDDIT}/{REDDITOR}'),
))
def test_create_file_name_formatter(test_file_scheme: str, test_folder_scheme: str, downloader_mock: MagicMock):
    downloader_mock.args.file_scheme = test_file_scheme
    downloader_mock.args.folder_scheme = test_folder_scheme
    result = RedditDownloader._create_file_name_formatter(downloader_mock)

    assert isinstance(result, FileNameFormatter)
    assert result.file_format_string == test_file_scheme
    assert result.directory_format_string == test_folder_scheme.split('/')


@pytest.mark.parametrize(('test_file_scheme', 'test_folder_scheme'), (
    ('', ''),
    ('', '{SUBREDDIT}'),
    ('test', '{SUBREDDIT}'),
))
def test_create_file_name_formatter_bad(test_file_scheme: str, test_folder_scheme: str, downloader_mock: MagicMock):
    downloader_mock.args.file_scheme = test_file_scheme
    downloader_mock.args.folder_scheme = test_folder_scheme
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
@pytest.mark.parametrize(('test_subreddits', 'limit', 'sort_type', 'time_filter', 'max_expected_len'), (
    (('Futurology',), 10, 'hot', 'all', 10),
    (('Futurology', 'Mindustry, Python'), 10, 'hot', 'all', 30),
    (('Futurology',), 20, 'hot', 'all', 20),
    (('Futurology', 'Python'), 10, 'hot', 'all', 20),
    (('Futurology',), 100, 'hot', 'all', 100),
    (('Futurology',), 0, 'hot', 'all', 0),
    (('Futurology',), 10, 'top', 'all', 10),
    (('Futurology',), 10, 'top', 'week', 10),
    (('Futurology',), 10, 'hot', 'week', 10),
))
def test_get_subreddit_normal(
        test_subreddits: list[str],
        limit: int,
        sort_type: str,
        time_filter: str,
        max_expected_len: int,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.args.limit = limit
    downloader_mock.args.sort = sort_type
    downloader_mock.args.subreddit = test_subreddits
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.sort_filter = RedditDownloader._create_sort_filter(downloader_mock)
    results = RedditDownloader._get_subreddits(downloader_mock)
    test_subreddits = downloader_mock._split_args_input(test_subreddits)
    results = [sub for res1 in results for sub in res1]
    assert all([isinstance(res1, praw.models.Submission) for res1 in results])
    assert all([res.subreddit.display_name in test_subreddits for res in results])
    assert len(results) <= max_expected_len


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_subreddits', 'search_term', 'limit', 'time_filter', 'max_expected_len'), (
    (('Python',), 'scraper', 10, 'all', 10),
    (('Python',), '', 10, 'all', 10),
    (('Python',), 'djsdsgewef', 10, 'all', 0),
    (('Python',), 'scraper', 10, 'year', 10),
    (('Python',), 'scraper', 10, 'hour', 1),
))
def test_get_subreddit_search(
        test_subreddits: list[str],
        search_term: str,
        time_filter: str,
        limit: int,
        max_expected_len: int,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.args.limit = limit
    downloader_mock.args.search = search_term
    downloader_mock.args.subreddit = test_subreddits
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    downloader_mock.args.time = time_filter
    downloader_mock.time_filter = RedditDownloader._create_time_filter(downloader_mock)
    results = RedditDownloader._get_subreddits(downloader_mock)
    results = [sub for res in results for sub in res]
    assert all([isinstance(res, praw.models.Submission) for res in results])
    assert all([res.subreddit.display_name in test_subreddits for res in results])
    assert len(results) <= max_expected_len


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
        downloader_mock: MagicMock,
):
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    downloader_mock.args.limit = limit
    downloader_mock.args.multireddit = test_multireddits
    downloader_mock.args.user = test_user
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock._create_filtered_listing_generator.return_value = \
        RedditDownloader._create_filtered_listing_generator(
            downloader_mock,
            reddit_instance.multireddit(test_user, test_multireddits[0]),
        )
    results = RedditDownloader._get_multireddits(downloader_mock)
    results = [sub for res in results for sub in res]
    assert all([isinstance(res, praw.models.Submission) for res in results])
    assert len(results) == limit


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
    downloader_mock._create_filtered_listing_generator.return_value = \
        RedditDownloader._create_filtered_listing_generator(
            downloader_mock,
            reddit_instance.redditor(test_user).submissions,
        )
    results = RedditDownloader._get_user_data(downloader_mock)
    results = assert_all_results_are_submissions(limit, results)
    assert all([res.author.name == test_user for res in results])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.parametrize('test_flag', (
    'upvoted',
    'saved',
))
def test_get_user_authenticated_lists(
    test_flag: str,
    downloader_mock: MagicMock,
    authenticated_reddit_instance: praw.Reddit,
):
    downloader_mock.args.__dict__[test_flag] = True
    downloader_mock.reddit_instance = authenticated_reddit_instance
    downloader_mock.args.user = 'me'
    downloader_mock.args.limit = 10
    downloader_mock._determine_sort_function.return_value = praw.models.Subreddit.hot
    downloader_mock.sort_filter = RedditTypes.SortType.HOT
    RedditDownloader._resolve_user_name(downloader_mock)
    results = RedditDownloader._get_user_data(downloader_mock)
    assert_all_results_are_submissions(10, results)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_files_len'), (
    ('ljyy27', 4),
))
def test_download_submission(
        test_submission_id: str,
        expected_files_len: int,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
        tmp_path: Path):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ''
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    assert len(folder_contents) == expected_files_len


@pytest.mark.online
@pytest.mark.reddit
def test_download_submission_file_exists(
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
        tmp_path: Path,
        capsys: pytest.CaptureFixture
):
    setup_logging(3)
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ''
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id='m1hqw6')
    Path(tmp_path, 'Arneeman_Metagaming isn\'t always a bad thing_m1hqw6.png').touch()
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert len(folder_contents) == 1
    assert 'Arneeman_Metagaming isn\'t always a bad thing_m1hqw6.png already exists' in output.out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'test_hash'), (
    ('m1hqw6', 'a912af8905ae468e0121e9940f797ad7'),
))
def test_download_submission_hash_exists(
        test_submission_id: str,
        test_hash: str,
        downloader_mock: MagicMock,
        reddit_instance: praw.Reddit,
        tmp_path: Path,
        capsys: pytest.CaptureFixture
):
    setup_logging(3)
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ''
    downloader_mock.args.no_dupes = True
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    downloader_mock.master_hash_list = {test_hash: None}
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert len(folder_contents) == 0
    assert re.search(r'Resource hash .*? downloaded elsewhere', output.out)


@pytest.mark.parametrize(('test_name', 'expected'), (
    ('Mindustry', 'Mindustry'),
    ('Futurology', 'Futurology'),
    ('r/Mindustry', 'Mindustry'),
    ('TrollXChromosomes', 'TrollXChromosomes'),
    ('r/TrollXChromosomes', 'TrollXChromosomes'),
    ('https://www.reddit.com/r/TrollXChromosomes/', 'TrollXChromosomes'),
    ('https://www.reddit.com/r/TrollXChromosomes', 'TrollXChromosomes'),
    ('https://www.reddit.com/r/Futurology/', 'Futurology'),
    ('https://www.reddit.com/r/Futurology', 'Futurology'),
))
def test_sanitise_subreddit_name(test_name: str, expected: str):
    result = RedditDownloader._sanitise_subreddit_name(test_name)
    assert result == expected


def test_search_existing_files():
    results = RedditDownloader.scan_existing_files(Path('.'))
    assert len(results.keys()) >= 40


@pytest.mark.parametrize(('test_subreddit_entries', 'expected'), (
    (['test1', 'test2', 'test3'], {'test1', 'test2', 'test3'}),
    (['test1,test2', 'test3'], {'test1', 'test2', 'test3'}),
    (['test1, test2', 'test3'], {'test1', 'test2', 'test3'}),
    (['test1; test2', 'test3'], {'test1', 'test2', 'test3'}),
    (['test1, test2', 'test1,test2,test3', 'test4'], {'test1', 'test2', 'test3', 'test4'})
))
def test_split_subreddit_entries(test_subreddit_entries: list[str], expected: set[str]):
    results = RedditDownloader._split_args_input(test_subreddit_entries)
    assert results == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_submission_id', (
    'm1hqw6',
))
def test_mark_hard_link(
        test_submission_id: str,
        downloader_mock: MagicMock,
        tmp_path: Path,
        reddit_instance: praw.Reddit
):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.args.make_hard_links = True
    downloader_mock.download_directory = tmp_path
    downloader_mock.args.folder_scheme = ''
    downloader_mock.args.file_scheme = '{POSTID}'
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    original = Path(tmp_path, f'{test_submission_id}.png')

    RedditDownloader._download_submission(downloader_mock, submission)
    assert original.exists()

    downloader_mock.args.file_scheme = 'test2_{POSTID}'
    downloader_mock.file_name_formatter = RedditDownloader._create_file_name_formatter(downloader_mock)
    RedditDownloader._download_submission(downloader_mock, submission)
    test_file_1_stats = original.stat()
    test_file_2_inode = Path(tmp_path, f'test2_{test_submission_id}.png').stat().st_ino

    assert test_file_1_stats.st_nlink == 2
    assert test_file_1_stats.st_ino == test_file_2_inode


@pytest.mark.parametrize(('test_ids', 'test_excluded', 'expected_len'), (
    (('aaaaaa',), (), 1),
    (('aaaaaa',), ('aaaaaa',), 0),
    ((), ('aaaaaa',), 0),
    (('aaaaaa', 'bbbbbb'), ('aaaaaa',), 1),
))
def test_excluded_ids(test_ids: tuple[str], test_excluded: tuple[str], expected_len: int, downloader_mock: MagicMock):
    downloader_mock.excluded_submission_ids = test_excluded
    test_submissions = []
    for test_id in test_ids:
        m = MagicMock()
        m.id = test_id
        test_submissions.append(m)
    downloader_mock.reddit_lists = [test_submissions]
    RedditDownloader.download(downloader_mock)
    assert downloader_mock._download_submission.call_count == expected_len


def test_read_excluded_submission_ids_from_file(downloader_mock: MagicMock, tmp_path: Path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('aaaaaa\nbbbbbb')
    downloader_mock.args.exclude_id_file = [test_file]
    results = RedditDownloader._read_excluded_ids(downloader_mock)
    assert results == {'aaaaaa', 'bbbbbb'}


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_redditor_name', (
    'Paracortex',
    'crowdstrike',
    'HannibalGoddamnit',
))
def test_check_user_existence_good(
    test_redditor_name: str,
    reddit_instance: praw.Reddit,
    downloader_mock: MagicMock,
):
    downloader_mock.reddit_instance = reddit_instance
    RedditDownloader._check_user_existence(downloader_mock, test_redditor_name)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_redditor_name', (
    'lhnhfkuhwreolo',
    'adlkfmnhglojh',
))
def test_check_user_existence_nonexistent(
        test_redditor_name: str,
        reddit_instance: praw.Reddit,
        downloader_mock: MagicMock,
):
    downloader_mock.reddit_instance = reddit_instance
    with pytest.raises(BulkDownloaderException, match='Could not find'):
        RedditDownloader._check_user_existence(downloader_mock, test_redditor_name)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_redditor_name', (
    'Bree-Boo',
))
def test_check_user_existence_banned(
        test_redditor_name: str,
        reddit_instance: praw.Reddit,
        downloader_mock: MagicMock,
):
    downloader_mock.reddit_instance = reddit_instance
    with pytest.raises(BulkDownloaderException, match='is banned'):
        RedditDownloader._check_user_existence(downloader_mock, test_redditor_name)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_subreddit_name', 'expected_message'), (
    ('donaldtrump', 'cannot be found'),
    ('submitters', 'private and cannot be scraped')
))
def test_check_subreddit_status_bad(test_subreddit_name: str, expected_message: str, reddit_instance: praw.Reddit):
    test_subreddit = reddit_instance.subreddit(test_subreddit_name)
    with pytest.raises(BulkDownloaderException, match=expected_message):
        RedditDownloader._check_subreddit_status(test_subreddit)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_subreddit_name', (
    'Python',
    'Mindustry',
    'TrollXChromosomes',
    'all',
))
def test_check_subreddit_status_good(test_subreddit_name: str, reddit_instance: praw.Reddit):
    test_subreddit = reddit_instance.subreddit(test_subreddit_name)
    RedditDownloader._check_subreddit_status(test_subreddit)
