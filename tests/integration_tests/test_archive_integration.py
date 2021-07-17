#!/usr/bin/env python3
# coding=utf-8

import re
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from bdfr.__main__ import cli

does_test_config_exist = Path('../test_config.cfg').exists()


def copy_test_config(run_path: Path):
    shutil.copy(Path('../test_config.cfg'), Path(run_path, '../test_config.cfg'))


def create_basic_args_for_archive_runner(test_args: list[str], run_path: Path):
    copy_test_config(run_path)
    out = [
        'archive',
        str(run_path),
        '-v',
        '--config', str(Path(run_path, '../test_config.cfg')),
        '--log', str(Path(run_path, 'test_log.txt')),
    ] + test_args
    return out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-l', 'gstd4hk'],
    ['-l', 'm2601g', '-f', 'yaml'],
    ['-l', 'n60t4c', '-f', 'xml'],
))
def test_cli_archive_single(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r'Writing entry .*? to file in .*? format', result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'Mindustry', '-L', 25],
    ['--subreddit', 'Mindustry', '-L', 25, '--format', 'xml'],
    ['--subreddit', 'Mindustry', '-L', 25, '--format', 'yaml'],
    ['--subreddit', 'Mindustry', '-L', 25, '--sort', 'new'],
    ['--subreddit', 'Mindustry', '-L', 25, '--time', 'day'],
    ['--subreddit', 'Mindustry', '-L', 25, '--time', 'day', '--sort', 'new'],
))
def test_cli_archive_subreddit(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r'Writing entry .*? to file in .*? format', result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'me', '--authenticate', '--all-comments', '-L', '10'],
    ['--user', 'me', '--user', 'djnish', '--authenticate', '--all-comments', '-L', '10'],
))
def test_cli_archive_all_user_comments(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--comment-context', '--link', 'gxqapql'],
))
def test_cli_archive_full_context(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Converting comment' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'all', '-L', 100],
    ['--subreddit', 'all', '-L', 100, '--sort', 'new'],
))
def test_cli_archive_long(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r'Writing entry .*? to file in .*? format', result.output)
