#!/usr/bin/env python3

import shutil
from pathlib import Path
from sys import platform
from unittest.mock import MagicMock, patch

import prawcore
import pytest
from click.testing import CliRunner

from bdfr.__main__ import cli

does_test_config_exist = Path("./tests/test_config.cfg").exists()


def copy_test_config(run_path: Path):
    shutil.copy(Path("./tests/test_config.cfg"), Path(run_path, "test_config.cfg"))


def create_basic_args_for_download_runner(test_args: list[str], run_path: Path):
    copy_test_config(run_path)
    out = [
        "download",
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
        ["-s", "EmpireDidNothingWrong", "-L", 3],
        ["-s", "r/EmpireDidNothingWrong", "-L", 3],
        ["-s", "https://www.reddit.com/r/TrollXChromosomes/", "-L", 3],
        ["-s", "r/TrollXChromosomes/", "-L", 3],
        ["-s", "TrollXChromosomes/", "-L", 3],
        ["-s", "trollxchromosomes", "-L", 3],
        ["-s", "trollxchromosomes,EmpireDidNothingWrong,python", "-L", 3],
        ["-s", "trollxchromosomes, EmpireDidNothingWrong, python", "-L", 3],
        ["-s", "trollxchromosomes", "-L", 3, "--time", "day"],
        ["-s", "trollxchromosomes", "-L", 3, "--sort", "new"],
        ["-s", "trollxchromosomes", "-L", 3, "--time", "day", "--sort", "new"],
        ["-s", "trollxchromosomes", "-L", 3, "--search", "women"],
        ["-s", "trollxchromosomes", "-L", 3, "--time", "week", "--search", "women"],
        ["-s", "trollxchromosomes", "-L", 3, "--sort", "new", "--search", "women"],
        ["-s", "trollxchromosomes", "-L", 3, "--time", "week", "--sort", "new", "--search", "women"],
    ),
)
def test_cli_download_subreddits(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Added submissions from subreddit " in result.output
    assert "Downloaded submission" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-s", "hentai", "-L", 10, "--search", "red", "--authenticate"],
        ["--authenticate", "--subscribed", "-L", 10],
    ),
)
def test_cli_download_search_subreddits_authenticated(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Added submissions from subreddit " in result.output
    assert "Downloaded submission" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--subreddit", "friends", "-L", 10, "--authenticate"],))
def test_cli_download_user_specific_subreddits(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Added submissions from subreddit " in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "6l7778"],
        ["-l", "https://reddit.com/r/EmpireDidNothingWrong/comments/6l7778/technically_true/"],
        ["-l", "m3hxzd"],  # Really long title used to overflow filename limit
        ["-l", "m5bqkf"],  # Resource leading to a 404
    ),
)
def test_cli_download_links(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--user", "helen_darten", "-m", "cuteanimalpics", "-L", 10],
        ["--user", "helen_darten", "-m", "cuteanimalpics", "-L", 10, "--sort", "rising"],
        ["--user", "helen_darten", "-m", "cuteanimalpics", "-L", 10, "--time", "week"],
        ["--user", "helen_darten", "-m", "cuteanimalpics", "-L", 10, "--time", "week", "--sort", "rising"],
    ),
)
def test_cli_download_multireddit(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Added submissions from multireddit " in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--user", "helen_darten", "-m", "xxyyzzqwerty", "-L", 10],))
def test_cli_download_multireddit_nonexistent(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Failed to get submissions for multireddit" in result.output
    assert "received 404 HTTP response" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--user", "djnish", "--submitted", "--user", "FriesWithThat", "-L", 10],
        ["--user", "me", "--downvoted", "--authenticate", "-L", 10],
        ["--user", "me", "--upvoted", "--authenticate", "-L", 10],
        ["--user", "me", "--saved", "--authenticate", "-L", 10],
        ["--user", "me", "--submitted", "--authenticate", "-L", 10],
        ["--user", "djnish", "--submitted", "-L", 10],
        ["--user", "djnish", "--submitted", "-L", 10, "--time", "month"],
        ["--user", "djnish", "--submitted", "-L", 10, "--sort", "controversial"],
    ),
)
def test_cli_download_user_data_good(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Downloaded submission " in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.authenticated
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--user", "me", "-L", 10, "--folder-scheme", ""],))
def test_cli_download_user_data_bad_me_unauthenticated(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "To use 'me' as a user, an authenticated Reddit instance must be used" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--subreddit", "python", "-L", 1, "--search-existing"],))
def test_cli_download_search_existing(test_args: list[str], tmp_path: Path):
    Path(tmp_path, "test.txt").touch()
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Calculating hashes for" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--subreddit", "tumblr", "-L", "25", "--skip", "png", "--skip", "jpg"],
        ["--subreddit", "MaliciousCompliance", "-L", "25", "--skip", "txt"],
        ["--subreddit", "tumblr", "-L", "10", "--skip-domain", "i.redd.it"],
    ),
)
def test_cli_download_download_filters(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert any(string in result.output for string in ("Download filter removed ", "filtered due to URL"))


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--subreddit", "all", "-L", "100", "--sort", "new"],))
def test_cli_download_long(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--user", "sdclhgsolgjeroij", "--submitted", "-L", 10],
        ["--user", "me", "--upvoted", "-L", 10],
        ["--user", "sdclhgsolgjeroij", "--upvoted", "-L", 10],
        ["--subreddit", "submitters", "-L", 10],  # Private subreddit
        ["--subreddit", "donaldtrump", "-L", 10],  # Banned subreddit
        ["--user", "djnish", "--user", "helen_darten", "-m", "cuteanimalpics", "-L", 10],
        ["--subreddit", "friends", "-L", 10],
        ["-l", "ijy4ch"],  # user deleted post
        ["-l", "kw4wjm"],  # post from banned subreddit
    ),
)
def test_cli_download_soft_fail(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Downloaded" not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.slow
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--time", "random"],
        ["--sort", "random"],
    ),
)
def test_cli_download_hard_fail(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code != 0


def test_cli_download_use_default_config(tmp_path: Path):
    runner = CliRunner()
    test_args = ["download", "-vv", str(tmp_path), "--log", str(Path(tmp_path, "test_log.txt"))]
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["-l", "6l7778", "--exclude-id", "6l7778"],))
def test_cli_download_links_exclusion(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "in exclusion list" in result.output
    assert "Downloaded submission " not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "6l7778", "--skip-subreddit", "EmpireDidNothingWrong"],
        ["-s", "trollxchromosomes", "--skip-subreddit", "trollxchromosomes", "-L", "3"],
    ),
)
def test_cli_download_subreddit_exclusion(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "in skip list" in result.output
    assert "Downloaded submission " not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["--file-scheme", "{TITLE}"],
        ["--file-scheme", "{TITLE}_test_{SUBREDDIT}"],
    ),
)
def test_cli_download_file_scheme_warning(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Some files might not be downloaded due to name conflicts" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "n9w9fo", "--disable-module", "SelfPost"],
        ["-l", "nnb9vs", "--disable-module", "VReddit"],
    ),
)
def test_cli_download_disable_modules(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "skipped due to disabled module" in result.output
    assert "Downloaded submission" not in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
def test_cli_download_include_id_file(tmp_path: Path):
    test_file = Path(tmp_path, "include.txt")
    test_args = ["--include-id-file", str(test_file)]
    test_file.write_text("odr9wg\nody576")
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Downloaded submission" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--ignore-user", "ArjanEgges", "-l", "m3hxzd"],))
def test_cli_download_ignore_user(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Downloaded submission" not in result.output
    assert "being an ignored user" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    ("test_args", "was_filtered"),
    (
        (["-l", "w22m5l", "--min-score", "50000"], True),
        (["-l", "w22m5l", "--min-score", "1"], False),
        (["-l", "w22m5l", "--max-score", "1"], True),
        (["-l", "w22m5l", "--max-score", "50000"], False),
    ),
)
def test_cli_download_score_filter(test_args: list[str], was_filtered: bool, tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert ("filtered due to score" in result.output) == was_filtered


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize(
    ("test_args", "response"),
    (
        (["--user", "nasa", "--submitted"], 502),
        (["--user", "nasa", "--submitted"], 504),
    ),
)
def test_cli_download_user_reddit_server_error(test_args: list[str], response: int, tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
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
@pytest.mark.skipif(platform == "darwin", reason="Test hangs on macos github")
@pytest.mark.parametrize(
    "test_args",
    (
        ["-l", "102vd5i", "--filename-restriction-scheme", "windows"],
        ["-l", "m3hxzd", "--filename-restriction-scheme", "windows"],
    ),
)
def test_cli_download_explicit_filename_restriction_scheme(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "Downloaded submission" in result.output
    assert "Forcing Windows-compatible filenames" in result.output


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.skipif(not does_test_config_exist, reason="A test config file is required for integration tests")
@pytest.mark.parametrize("test_args", (["--link", "ehqt2g", "--link", "ehtuv8", "--no-dupes"],))
def test_cli_download_no_empty_dirs(test_args: list[str], tmp_path: Path):
    runner = CliRunner()
    test_args = create_basic_args_for_download_runner(test_args, tmp_path)
    result = runner.invoke(cli, test_args)
    assert result.exit_code == 0
    assert "downloaded elsewhere" in result.output
    assert Path(tmp_path, "EmpireDidNothingWrong").exists()
    assert not Path(tmp_path, "StarWarsEU").exists()
