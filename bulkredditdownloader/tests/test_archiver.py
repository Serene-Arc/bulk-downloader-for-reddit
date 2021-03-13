#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from unittest.mock import MagicMock

import praw
import pytest

from bulkredditdownloader.archive_entry import ArchiveEntry
from bulkredditdownloader.archiver import Archiver


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_submission_id', (
    'm3reby',
))
def test_write_submission_json(test_submission_id: str, tmp_path: Path, reddit_instance: praw.Reddit):
    archiver_mock = MagicMock()
    test_path = Path(tmp_path, 'test.json')
    test_submission = reddit_instance.submission(id=test_submission_id)
    archiver_mock.file_name_formatter.format_path.return_value = test_path
    test_entry = ArchiveEntry(test_submission)
    Archiver._write_submission_json(archiver_mock, test_entry)
    assert test_path.exists()


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_submission_id', (
    'm3reby',
))
def test_write_submission_xml(test_submission_id: str, tmp_path: Path, reddit_instance: praw.Reddit):
    archiver_mock = MagicMock()
    test_path = Path(tmp_path, 'test.xml')
    test_submission = reddit_instance.submission(id=test_submission_id)
    archiver_mock.file_name_formatter.format_path.return_value = test_path
    test_entry = ArchiveEntry(test_submission)
    Archiver._write_submission_xml(archiver_mock, test_entry)
    assert test_path.exists()


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize('test_submission_id', (
    'm3reby',
))
def test_write_submission_yaml(test_submission_id: str, tmp_path: Path, reddit_instance: praw.Reddit):
    archiver_mock = MagicMock()
    test_path = Path(tmp_path, 'test.yaml')
    test_submission = reddit_instance.submission(id=test_submission_id)
    archiver_mock.file_name_formatter.format_path.return_value = test_path
    test_entry = ArchiveEntry(test_submission)
    Archiver._write_submission_yaml(archiver_mock, test_entry)
    assert test_path.exists()
