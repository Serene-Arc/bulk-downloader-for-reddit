#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path

import pytest
from click.testing import CliRunner

from bulkredditdownloader.__main__ import cli


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-s', 'Mindustry', '-L', 1],
    ['-s', 'r/Mindustry', '-L', 1],
    ['-s', 'r/mindustry', '-L', 1],
    ['-s', 'mindustry', '-L', 1],
    ['-s', 'https://www.reddit.com/r/TrollXChromosomes/', '-L', 1],
    ['-s', 'r/TrollXChromosomes/', '-L', 1],
    ['-s', 'TrollXChromosomes/', '-L', 1],
    ['-s', 'trollxchromosomes', '-L', 1],
    ['-s', 'trollxchromosomes', '-L', 1, '--time', 'day'],
    ['-s', 'trollxchromosomes', '-L', 1, '--sort', 'new'],
    ['-s', 'trollxchromosomes', '-L', 1, '--time', 'day', '--sort', 'new'],
    ['-s', 'trollxchromosomes', '-L', 1, '--search', 'women'],
    ['-s', 'trollxchromosomes', '-L', 1, '--time', 'day', '--search', 'women'],
    ['-s', 'trollxchromosomes', '-L', 1, '--sort', 'new', '--search', 'women'],
    ['-s', 'trollxchromosomes', '-L', 1, '--time', 'day', '--sort', 'new', '--search', 'women'],
))
def test_cli_download_subreddits(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Added submissions from subreddit ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-l', 'm2601g'],
    ['-l', 'https://www.reddit.com/r/TrollXChromosomes/comments/m2601g/its_a_step_in_the_right_direction/'],
))
def test_cli_download_links(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--sort', 'rising'],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--time', 'week'],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--time', 'week', '--sort', 'rising'],
))
def test_cli_download_multireddit(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Added submissions from multireddit ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'helen_darten', '-m', 'xxyyzzqwerty', '-L', 10],
))
def test_cli_download_multireddit_nonexistent(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Failed to get submissions for multireddit' in result.output
    assert 'received 404 HTTP response' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'me', '--upvoted', '--authenticate', '-L', 10],
    ['--user', 'me', '--saved', '--authenticate', '-L', 10],
    ['--user', 'me', '--submitted', '--authenticate', '-L', 10],
    ['--user', 'djnish', '--submitted', '-L', 10],
    ['--user', 'djnish', '--submitted', '-L', 10, '--time', 'month'],
    ['--user', 'djnish', '--submitted', '-L', 10, '--sort', 'controversial'],
    ['--user', 'djnish', '--submitted', '-L', 10, '--sort', 'controversial', '--time', 'month'],
))
def test_cli_download_user_data_good(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Downloaded submission ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'me', '-L', 10, '--set-folder-scheme', ''],
))
def test_cli_download_user_data_bad_me_unauthenticated(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'To use "me" as a user, an authenticated Reddit instance must be used' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(Path('test_config.cfg') is False, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'python', '-L', 10, '--search-existing'],
))
def test_cli_download_search_existing(test_args: list[str], tmp_path: Path):
    Path(tmp_path, 'test.txt').touch()
    runner = CliRunner()
    test_args = ['download', str(tmp_path), '-v', '--config', 'test_config.cfg'] + test_args
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Calculating hashes for' in result.output
