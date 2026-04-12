#!/usr/bin/env python3

import re
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import prawcore
import pytest
from click.testing import CliRunner

from bdfr.__main__ import cli

does_test_config_exist = Path("./tests/test_config.cfg").exists()


def copy_test_config(run_path: Path):
    shutil.copy(Path("./tests/test_config.cfg"), Path(run_path, "test_config.cfg"))


def create_basic_args_for_archive_runner(test_args: list[str], run_path: Path):
    copy_test_config(run_path)
    out = [
        "archive",
        str(run_path),
        "-v",
        "--config",
        str(Path(run_path, "test_config.cfg")),
        "--log",
        str(Path(run_path, "test_log.txt")),
        *test_args,
    ]
    return out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "gstd4hk"],
        ["-l", "m2601g", "-f", "yaml"],
        ["-l", "n60t4c", "-f", "xml"],
    ),
)
def test_cli_archive_single(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r"Writing entry .*? to file in .*? format", result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (["-l", "m2601g", "-f", "yaml", "-f", "json"],),
)
def test_cli_archive_single_multi_format(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r"Writing entry .*? to file in YAML format", result.output)
    assert re.search(r"Writing entry .*? to file in JSON format", result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--subreddit", "Mindustry", "-L", 25],
        ["--subreddit", "Mindustry", "-L", 25, "--format", "xml"],
        ["--subreddit", "Mindustry", "-L", 25, "--format", "yaml"],
        ["--subreddit", "Mindustry", "-L", 25, "--sort", "new"],
        ["--subreddit", "Mindustry", "-L", 25, "--time", "day"],
        ["--subreddit", "Mindustry", "-L", 25, "--time", "day", "--sort", "new"],
    ),
)
def test_cli_archive_subreddit(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r"Writing entry .*? to file in .*? format", result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--user", "me", "--authenticate", "--all-comments", "-L", "10"],
        ["--user", "me", "--user", "djnish", "--authenticate", "--all-comments", "-L", "10"],
    ),
)
def test_cli_archive_all_user_comments(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--comment-context", "--link", "gxqapql"],))
def test_cli_archive_full_context(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Converting comment" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--subreddit", "all", "-L", 100],
        ["--subreddit", "all", "-L", 100, "--sort", "new"],
    ),
)
def test_cli_archive_long(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert re.search(r"Writing entry .*? to file in .*? format", result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--ignore-user", "ArjanEgges", "-l", "m3hxzd"],))
def test_cli_archive_ignore_user(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "being an ignored user" in result.output
    assert "Attempting to archive submission" not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--file-scheme", "{TITLE}", "-l", "suy011"],))
def test_cli_archive_file_format(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Attempting to archive submission" in result.output
    assert re.search("format at /.+?/Judge says Trump and two adult", result.output)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["-l", "m2601g", "--exclude-id", "m2601g"],))
def test_cli_archive_links_exclusion(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "in exclusion list" in result.output
    assert "Attempting to archive" not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "ijy4ch"],  # user deleted post
        ["-l", "kw4wjm"],  # post from banned subreddit
    ),
)
def test_cli_archive_soft_fail(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "failed to be archived due to a PRAW exception" in result.output
    assert "Attempting to archive" not in result.output


@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    ("test_args", "response"),
    (
        (["--user", "nasa", "--submitted"], 502),
        (["--user", "nasa", "--submitted"], 504),
    ),
)
def test_user_serv_fail(test_args: list[str], response: int, tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    with patch("bdfr.connector.sleep", return_value=None):
        with patch(
            "bdfr.connector.RedditConnector.check_user_existence",
            side_effect=prawcore.exceptions.ResponseException(MagicMock(status_code=response)),
        ):
            result = runner.invoke(cli, test_args)
            assert result.exit_code == 0
            assert f"received {response} HTTP response" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--skip-comments", "--link", "gxqapql"],))
def test_cli_archive_skip_comments(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_archive_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Converting comment" not in result.output
    assert "Retrieving full comment tree for submission" not in result.output
