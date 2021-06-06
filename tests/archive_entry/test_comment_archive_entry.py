#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.archive_entry.comment_archive_entry import CommentArchiveEntry


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_comment_id', 'expected_dict'), (
    ('gstd4hk', {
        'author': 'james_pic',
        'subreddit': 'Python',
        'submission': 'mgi4op',
        'submission_title': '76% Faster CPython',
        'distinguished': None,
    }),
))
def test_get_comment_details(test_comment_id: str, expected_dict: dict, reddit_instance: praw.Reddit):
    comment = reddit_instance.comment(id=test_comment_id)
    test_entry = CommentArchiveEntry(comment)
    result = test_entry.compile()
    assert all([result.get(key) == expected_dict[key] for key in expected_dict.keys()])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_comment_id', 'expected_min_comments'), (
    ('gstd4hk', 4),
    ('gsvyste', 3),
    ('gsxnvvb', 5),
))
def test_get_comment_replies(test_comment_id: str, expected_min_comments: int, reddit_instance: praw.Reddit):
    comment = reddit_instance.comment(id=test_comment_id)
    test_entry = CommentArchiveEntry(comment)
    result = test_entry.compile()
    assert len(result.get('replies')) >= expected_min_comments
