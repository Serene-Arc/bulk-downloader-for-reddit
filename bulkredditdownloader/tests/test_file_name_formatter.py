#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import praw.models
import pytest

from bulkredditdownloader.file_name_formatter import FileNameFormatter
from bulkredditdownloader.resource import Resource


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
    return test


@pytest.fixture()
def reddit_submission(reddit_instance) -> praw.models.Submission:
    return reddit_instance.submission(id='lgilgt')


@pytest.mark.parametrize(('format_string', 'expected'), (('{SUBREDDIT}', 'randomreddit'),
                                                         ('{REDDITOR}', 'person'),
                                                         ('{POSTID}', '12345'),
                                                         ('{UPVOTES}', '1000'),
                                                         ('{FLAIR}', 'test_flair'),
                                                         ('{DATE}', '123456789'),
                                                         ('{REDDITOR}_{TITLE}_{POSTID}', 'person_name_12345')
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
@pytest.mark.parametrize(('format_string', 'expected'),
                         (('{SUBREDDIT}', 'Mindustry'),
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
@pytest.mark.parametrize(('format_string_directory', 'format_string_file', 'expected'),
                         (('{SUBREDDIT}', '{POSTID}', 'test/Mindustry/lgilgt.png'),
                          ('{SUBREDDIT}', '{TITLE}_{POSTID}',
                           'test/Mindustry/Toxopid that is NOT humane >:(_lgilgt.png'),
                          ('{SUBREDDIT}', '{REDDITOR}_{TITLE}_{POSTID}',
                           'test/Mindustry/Gamer_player_boi_Toxopid that is NOT humane >:(_lgilgt.png')
                          ))
def test_format_full(
        format_string_directory: str,
        format_string_file: str,
        expected: str,
        reddit_submission: praw.models.Submission):
    test_resource = Resource(reddit_submission, 'i.reddit.com/blabla.png')
    test_formatter = FileNameFormatter(format_string_file, format_string_directory)
    result = test_formatter._format_path(test_resource, Path('test'))
    assert str(result) == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('format_string_directory', 'format_string_file', 'index', 'expected'),
                         (('{SUBREDDIT}', '{POSTID}', None, 'test/Mindustry/lgilgt.png'),
                          ('{SUBREDDIT}', '{POSTID}', 1, 'test/Mindustry/lgilgt_1.png'),
                          ('{SUBREDDIT}', '{POSTID}', 2, 'test/Mindustry/lgilgt_2.png'),
                          ('{SUBREDDIT}', '{TITLE}_{POSTID}', 2,
                           'test/Mindustry/Toxopid that is NOT humane >:(_lgilgt_2.png'),
                          ))
def test_format_full_with_index_suffix(
        format_string_directory: str,
        format_string_file: str,
        index: Optional[int],
        expected: str,
        reddit_submission: praw.models.Submission):
    test_resource = Resource(reddit_submission, 'i.reddit.com/blabla.png')
    test_formatter = FileNameFormatter(format_string_file, format_string_directory)
    result = test_formatter._format_path(test_resource, Path('test'), index)
    assert str(result) == expected


def test_format_multiple_resources():
    mocks = []
    for i in range(1, 5):
        new_mock = MagicMock()
        new_mock.url = 'https://example.com/test.png'
        new_mock.extension = '.png'
        new_mock.source_submission.title = 'test'
        mocks.append(new_mock)
    test_formatter = FileNameFormatter('{TITLE}', '')
    results = test_formatter.format_resource_paths(mocks, Path('.'))
    results = set([str(res[0]) for res in results])
    assert results == {'test_1.png', 'test_2.png', 'test_3.png', 'test_4.png'}
