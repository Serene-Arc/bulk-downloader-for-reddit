#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import praw.models
import pytest

from bdfr.file_name_formatter import FileNameFormatter
from bdfr.resource import Resource


@pytest.fixture()
def submission() -> MagicMock:
    test = MagicMock()
    test.title = 'name'
    test.subreddit.display_name = 'randomreddit'
    test.author.name = 'person'
    test.id = '12345'
    test.score = 1000
    test.link_flair_text = 'test_flair'
    test.created_utc = 123456789
    test.__class__ = praw.models.Submission
    return test


@pytest.fixture(scope='session')
def reddit_submission(reddit_instance: praw.Reddit) -> praw.models.Submission:
    return reddit_instance.submission(id='lgilgt')


@pytest.mark.parametrize(('format_string', 'expected'), (
    ('{SUBREDDIT}', 'randomreddit'),
    ('{REDDITOR}', 'person'),
    ('{POSTID}', '12345'),
    ('{UPVOTES}', '1000'),
    ('{FLAIR}', 'test_flair'),
    ('{DATE}', '123456789'),
    ('{REDDITOR}_{TITLE}_{POSTID}', 'person_name_12345'),
    ('{RANDOM}', '{RANDOM}'),
))
def test_format_name_mock(format_string: str, expected: str, submission: MagicMock):
    result = FileNameFormatter._format_name(submission, format_string)
    assert result == expected


@pytest.mark.parametrize(('test_string', 'expected'), (
    ('', False),
    ('test', False),
    ('{POSTID}', True),
    ('POSTID', False),
    ('{POSTID}_test', True),
    ('test_{TITLE}', True),
    ('TITLE_POSTID', False),
))
def test_check_format_string_validity(test_string: str, expected: bool):
    result = FileNameFormatter.validate_string(test_string)
    assert result == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('format_string', 'expected'), (
    ('{SUBREDDIT}', 'Mindustry'),
    ('{REDDITOR}', 'Gamer_player_boi'),
    ('{POSTID}', 'lgilgt'),
    ('{FLAIR}', 'Art'),
    ('{SUBREDDIT}_{TITLE}', 'Mindustry_Toxopid that is NOT humane >:('),
    ('{REDDITOR}_{TITLE}_{POSTID}', 'Gamer_player_boi_Toxopid that is NOT humane >:(_lgilgt')
))
def test_format_name_real(format_string: str, expected: str, reddit_submission: praw.models.Submission):
    result = FileNameFormatter._format_name(reddit_submission, format_string)
    assert result == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('format_string_directory', 'format_string_file', 'expected'), (
    (
        '{SUBREDDIT}',
        '{POSTID}',
        'test/Mindustry/lgilgt.png',
    ),
    (
        '{SUBREDDIT}',
        '{TITLE}_{POSTID}',
        'test/Mindustry/Toxopid that is NOT humane >:(_lgilgt.png',
    ),
    (
        '{SUBREDDIT}',
        '{REDDITOR}_{TITLE}_{POSTID}',
        'test/Mindustry/Gamer_player_boi_Toxopid that is NOT humane >:(_lgilgt.png',
    ),
))
def test_format_full(
        format_string_directory: str,
        format_string_file: str,
        expected: str,
        reddit_submission: praw.models.Submission):
    test_resource = Resource(reddit_submission, 'i.reddit.com/blabla.png')
    test_formatter = FileNameFormatter(format_string_file, format_string_directory)
    result = test_formatter.format_path(test_resource, Path('test'))
    assert str(result) == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('format_string_directory', 'format_string_file'), (
    ('{SUBREDDIT}', '{POSTID}'),
    ('{SUBREDDIT}', '{UPVOTES}'),
    ('{SUBREDDIT}', '{UPVOTES}{POSTID}'),
))
def test_format_full_conform(
        format_string_directory: str,
        format_string_file: str,
        reddit_submission: praw.models.Submission):
    test_resource = Resource(reddit_submission, 'i.reddit.com/blabla.png')
    test_formatter = FileNameFormatter(format_string_file, format_string_directory)
    test_formatter.format_path(test_resource, Path('test'))


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('format_string_directory', 'format_string_file', 'index', 'expected'), (
    ('{SUBREDDIT}', '{POSTID}', None, 'test/Mindustry/lgilgt.png'),
    ('{SUBREDDIT}', '{POSTID}', 1, 'test/Mindustry/lgilgt_1.png'),
    ('{SUBREDDIT}', '{POSTID}', 2, 'test/Mindustry/lgilgt_2.png'),
    ('{SUBREDDIT}', '{TITLE}_{POSTID}', 2, 'test/Mindustry/Toxopid that is NOT humane >:(_lgilgt_2.png'),
))
def test_format_full_with_index_suffix(
        format_string_directory: str,
        format_string_file: str,
        index: Optional[int],
        expected: str,
        reddit_submission: praw.models.Submission,
):
    test_resource = Resource(reddit_submission, 'i.reddit.com/blabla.png')
    test_formatter = FileNameFormatter(format_string_file, format_string_directory)
    result = test_formatter.format_path(test_resource, Path('test'), index)
    assert str(result) == expected


def test_format_multiple_resources():
    mocks = []
    for i in range(1, 5):
        new_mock = MagicMock()
        new_mock.url = 'https://example.com/test.png'
        new_mock.extension = '.png'
        new_mock.source_submission.title = 'test'
        new_mock.source_submission.__class__ = praw.models.Submission
        mocks.append(new_mock)
    test_formatter = FileNameFormatter('{TITLE}', '')
    results = test_formatter.format_resource_paths(mocks, Path('.'))
    results = set([str(res[0]) for res in results])
    assert results == {'test_1.png', 'test_2.png', 'test_3.png', 'test_4.png'}


@pytest.mark.parametrize(('test_filename', 'test_ending'), (
    ('A' * 300, '.png'),
    ('A' * 300, '_1.png'),
    ('a' * 300, '_1000.jpeg'),
    ('😍💕✨' * 100, '_1.png'),
))
def test_limit_filename_length(test_filename: str, test_ending: str):
    result = FileNameFormatter._limit_file_name_length(test_filename, test_ending)
    assert len(result) <= 255
    assert len(result.encode('utf-8')) <= 255
    assert isinstance(result, str)


@pytest.mark.parametrize(('test_filename', 'test_ending', 'expected_end'), (
    ('test_aaaaaa', '_1.png', 'test_aaaaaa_1.png'),
    ('test_aataaa', '_1.png', 'test_aataaa_1.png'),
    ('test_abcdef', '_1.png', 'test_abcdef_1.png'),
    ('test_aaaaaa', '.png', 'test_aaaaaa.png'),
    ('test', '_1.png', 'test_1.png'),
    ('test_m1hqw6', '_1.png', 'test_m1hqw6_1.png'),
    ('A' * 300 + '_bbbccc', '.png', '_bbbccc.png'),
    ('A' * 300 + '_bbbccc', '_1000.jpeg', '_bbbccc_1000.jpeg'),
    ('😍💕✨' * 100 + '_aaa1aa', '_1.png', '_aaa1aa_1.png'),
))
def test_preserve_id_append_when_shortening(test_filename: str, test_ending: str, expected_end: str):
    result = FileNameFormatter._limit_file_name_length(test_filename, test_ending)
    assert len(result) <= 255
    assert len(result.encode('utf-8')) <= 255
    assert isinstance(result, str)
    assert result.endswith(expected_end)


def test_shorten_filenames(submission: MagicMock, tmp_path: Path):
    submission.title = 'A' * 300
    submission.author.name = 'test'
    submission.subreddit.display_name = 'test'
    submission.id = 'BBBBBB'
    test_resource = Resource(submission, 'www.example.com/empty', '.jpeg')
    test_formatter = FileNameFormatter('{REDDITOR}_{TITLE}_{POSTID}', '{SUBREDDIT}')
    result = test_formatter.format_path(test_resource, tmp_path)
    result.parent.mkdir(parents=True)
    result.touch()


@pytest.mark.parametrize(('test_string', 'expected'), (
    ('test', 'test'),
    ('test😍', 'test'),
    ('test.png', 'test.png'),
    ('test*', 'test'),
    ('test**', 'test'),
    ('test?*', 'test'),
    ('test_???.png', 'test_.png'),
    ('test_???😍.png', 'test_.png'),
))
def test_format_file_name_for_windows(test_string: str, expected: str):
    result = FileNameFormatter._format_for_windows(test_string)
    assert result == expected


@pytest.mark.parametrize(('test_string', 'expected'), (
    ('test', 'test'),
    ('test😍', 'test'),
    ('😍', ''),
))
def test_strip_emojies(test_string: str, expected: str):
    result = FileNameFormatter._strip_emojis(test_string)
    assert result == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected'), (
    ('mfuteh', {
        'title': 'Why Do Interviewers Ask Linked List Questions?',
        'redditor': 'mjgardner',
    }),
))
def test_generate_dict_for_submission(test_submission_id: str, expected: dict, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    result = FileNameFormatter._generate_name_dict_from_submission(test_submission)
    assert all([result.get(key) == expected[key] for key in expected.keys()])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_comment_id', 'expected'), (
    ('gsq0yuw', {
        'title': 'Why Do Interviewers Ask Linked List Questions?',
        'redditor': 'Doctor-Dapper',
        'postid': 'gsq0yuw',
        'flair': '',
    }),
))
def test_generate_dict_for_comment(test_comment_id: str, expected: dict, reddit_instance: praw.Reddit):
    test_comment = reddit_instance.comment(id=test_comment_id)
    result = FileNameFormatter._generate_name_dict_from_comment(test_comment)
    assert all([result.get(key) == expected[key] for key in expected.keys()])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_file_scheme', 'test_folder_scheme', 'test_comment_id', 'expected_name'), (
    ('{POSTID}', '', 'gsoubde', 'gsoubde.json'),
    ('{REDDITOR}_{POSTID}', '', 'gsoubde', 'DELETED_gsoubde.json'),
))
def test_format_archive_entry_comment(
        test_file_scheme: str,
        test_folder_scheme: str,
        test_comment_id: str,
        expected_name: str,
        tmp_path: Path,
        reddit_instance: praw.Reddit,
):
    test_comment = reddit_instance.comment(id=test_comment_id)
    test_formatter = FileNameFormatter(test_file_scheme, test_folder_scheme)
    test_entry = Resource(test_comment, '', '.json')
    result = test_formatter.format_path(test_entry, tmp_path)
    assert result.name == expected_name


@pytest.mark.parametrize(('test_folder_scheme', 'expected'), (
    ('{REDDITOR}/{SUBREDDIT}', 'person/randomreddit'),
    ('{POSTID}/{SUBREDDIT}/{REDDITOR}', '12345/randomreddit/person'),
))
def test_multilevel_folder_scheme(
        test_folder_scheme: str,
        expected: str,
        tmp_path: Path,
        submission: MagicMock,
):
    test_formatter = FileNameFormatter('{POSTID}', test_folder_scheme)
    test_resource = MagicMock()
    test_resource.source_submission = submission
    test_resource.extension = '.png'
    result = test_formatter.format_path(test_resource, tmp_path)
    result = result.relative_to(tmp_path)
    assert str(result.parent) == expected
    assert len(result.parents) == (len(expected.split('/')) + 1)


@pytest.mark.parametrize(('test_name_string', 'expected'), (
    ('test', 'test'),
    ('😍', '😍'),
    ('test😍', 'test😍'),
    ('test😍 ’', 'test😍 ’'),
    ('test😍 \\u2019', 'test😍 ’'),
    ('Using that real good [1\\4]', 'Using that real good [1\\4]'),
))
def test_preserve_emojis(test_name_string: str, expected: str, submission: MagicMock):
    submission.title = test_name_string
    result = FileNameFormatter._format_name(submission, '{TITLE}')
    assert result == expected


@pytest.mark.parametrize(('test_string', 'expected'), (
    ('test \\u2019', 'test ’'),
    ('My cat\\u2019s paws are so cute', 'My cat’s paws are so cute'),
))
def test_convert_unicode_escapes(test_string: str, expected: str):
    result = FileNameFormatter._convert_unicode_escapes(test_string)
    assert result == expected
