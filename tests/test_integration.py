#!/usr/bin/env python3
# coding=utf-8

import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from bdfr.__main__ import cli

does_test_config_exist = Path('test_config.cfg').exists()


def create_basic_args_for_download_runner(test_args: list[str], tmp_path: Path):
    out = [
        'download', str(tmp_path),
        '-v',
        '--config', 'test_config.cfg',
        '--log', str(Path(tmp_path, 'test_log.txt')),
    ] + test_args
    return out


def create_basic_args_for_archive_runner(test_args: list[str], tmp_path: Path):
    out = [
        'archive',
        str(tmp_path),
        '-v',
        '--config', 'test_config.cfg',
        '--log', str(Path(tmp_path, 'test_log.txt')),
    ] + test_args
    return out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-s', 'Mindustry', '-L', 1],
    ['-s', 'r/Mindustry', '-L', 1],
    ['-s', 'r/mindustry', '-L', 1],
    ['-s', 'mindustry', '-L', 1],
    ['-s', 'https://www.reddit.com/r/TrollXChromosomes/', '-L', 1],
    ['-s', 'r/TrollXChromosomes/', '-L', 1],
    ['-s', 'TrollXChromosomes/', '-L', 1],
    ['-s', 'trollxchromosomes', '-L', 1],
    ['-s', 'trollxchromosomes,mindustry,python', '-L', 1],
    ['-s', 'trollxchromosomes, mindustry, python', '-L', 1],
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
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Added submissions from subreddit ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-l', 'm2601g'],
    ['-l', 'https://www.reddit.com/r/TrollXChromosomes/comments/m2601g/its_a_step_in_the_right_direction/'],
    ['-l', 'm3hxzd'],  # Really long title used to overflow filename limit
    ['-l', 'm3kua3'],  # Has a deleted user
    ['-l', 'm5bqkf'],  # Resource leading to a 404
))
def test_cli_download_links(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--sort', 'rising'],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--time', 'week'],
    ['--user', 'helen_darten', '-m', 'cuteanimalpics', '-L', 10, '--time', 'week', '--sort', 'rising'],
))
def test_cli_download_multireddit(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Added submissions from multireddit ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'helen_darten', '-m', 'xxyyzzqwerty', '-L', 10],
))
def test_cli_download_multireddit_nonexistent(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Failed to get submissions for multireddit' in result.output
    assert 'received 404 HTTP response' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'me', '--upvoted', '--authenticate', '-L', 10],
    ['--user', 'me', '--saved', '--authenticate', '-L', 10],
    ['--user', 'me', '--submitted', '--authenticate', '-L', 10],
    ['--user', 'djnish', '--submitted', '-L', 10],
    ['--user', 'djnish', '--submitted', '-L', 10, '--time', 'month'],
    ['--user', 'djnish', '--submitted', '-L', 10, '--sort', 'controversial'],
))
def test_cli_download_user_data_good(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Downloaded submission ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'me', '-L', 10, '--folder-scheme', ''],
))
def test_cli_download_user_data_bad_me_unauthenticated(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'To use "me" as a user, an authenticated Reddit instance must be used' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'python', '-L', 10, '--search-existing'],
))
def test_cli_download_search_existing(test_args: list[str], tmp_path: Path):
    Path(tmp_path, 'test.txt').touch()
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Calculating hashes for' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'tumblr', '-L', '25', '--skip', 'png', '--skip', 'jpg'],
    ['--subreddit', 'MaliciousCompliance', '-L', '25', '--skip', 'txt'],
))
def test_cli_download_download_filters(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Download filter removed ' in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--subreddit', 'all', '-L', '100', '--sort', 'new'],
))
def test_cli_download_long(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


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
))
def test_cli_archive_all_user_comments(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


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


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--user', 'sdclhgsolgjeroij', '--submitted', '-L', 10],
    ['--user', 'me', '--upvoted', '-L', 10],
    ['--user', 'sdclhgsolgjeroij', '--upvoted', '-L', 10],
    ['--subreddit', 'submitters', '-L', 10],  # Private subreddit
    ['--subreddit', 'donaldtrump', '-L', 10],  # Banned subreddit
))
def test_cli_download_soft_fail(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--time', 'random'],
    ['--sort', 'random'],
))
def test_cli_download_hard_fail(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code != 0


def test_cli_download_use_default_config(tmp_path: Path):
    runner = CliRunner()
    test_args = ['download', '-vv', str(tmp_path)]
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-l', 'm2601g', '--exclude-id', 'm2601g'],
))
def test_cli_download_links_exclusion(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'in exclusion list' in result.output
    assert 'Downloaded submission ' not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['-l', 'm2601g', '--skip-subreddit', 'trollxchromosomes'],
    ['-s', 'trollxchromosomes', '--skip-subreddit', 'trollxchromosomes', '-L', '3'],
))
def test_cli_download_subreddit_exclusion(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'in skip list' in result.output
    assert 'Downloaded submission ' not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason='A test config file is required for integration tests')
@pytest.mark.parametrize('test_args', (
    ['--file-scheme', '{TITLE}'],
    ['--file-scheme', '{TITLE}_test_{SUBREDDIT}'],
))
def test_cli_file_scheme_warning(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Some files might not be downloaded due to name conflicts' in result.output
