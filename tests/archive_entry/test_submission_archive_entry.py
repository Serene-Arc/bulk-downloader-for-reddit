#!/usr/bin/env python3
# coding=utf-8

import praw
import pytest

from bdfr.archive_entry.submission_archive_entry import SubmissionArchiveEntry


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'min_comments'), (
    ('m3reby', 27),
))
def test_get_comments(test_submission_id: str, min_comments: int, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    test_archive_entry = SubmissionArchiveEntry(test_submission)
    results = test_archive_entry._get_comments()
    assert len(results) >= min_comments


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'expected_dict'), (
    ('m3reby', {
        'author': 'sinjen-tos',
        'id': 'm3reby',
        'link_flair_text': 'image',
        'pinned': False,
        'spoiler': False,
        'over_18': False,
        'locked': False,
        'distinguished': None,
        'created_utc': 1615583837,
        'permalink': '/r/australia/comments/m3reby/this_little_guy_fell_out_of_a_tree_and_in_front/'
    }),
    ('m3kua3', {'author': 'DELETED'}),
))
def test_get_post_details(test_submission_id: str, expected_dict: dict, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    test_archive_entry = SubmissionArchiveEntry(test_submission)
    test_archive_entry._get_post_details()
    assert all([test_archive_entry.post_details.get(key) == expected_dict[key] for key in expected_dict.keys()])
