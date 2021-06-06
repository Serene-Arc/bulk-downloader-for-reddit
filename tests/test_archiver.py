#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from unittest.mock import MagicMock

import praw
import pytest

from bdfr.archiver import Archiver


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(('test_submission_id', 'test_format'), (
    ('m3reby', 'xml'),
    ('m3reby', 'json'),
    ('m3reby', 'yaml'),
))
def test_write_submission_json(test_submission_id: str, tmp_path: Path, test_format: str, reddit_instance: praw.Reddit):
    archiver_mock = MagicMock()
    archiver_mock.args.format = test_format
    test_path = Path(tmp_path, 'test')
    test_submission = reddit_instance.submission(id=test_submission_id)
    archiver_mock.file_name_formatter.format_path.return_value = test_path
    Archiver.write_entry(archiver_mock, test_submission)
