#!/usr/bin/env python3
# coding=utf-8

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from bdfr.__main__ import cli

does_test_config_exist = Path('../test_config.cfg').exists()


def copy_test_config(run_path: Path):
    shutil.copy(Path('../test_config.cfg'), Path(run_path, '../test_config.cfg'))


def create_basic_args_for_cloner_runner(test_args: list[str], tmp_path: Path):
    out = [
        'clone',
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
    ['-l', 'm2601g'],
    ['-s', 'TrollXChromosomes/', '-L', 1],
))
def test_cli_scrape_general(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_cloner_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert 'Downloaded submission' in result.output
    assert 'Record for entry item' in result.output
