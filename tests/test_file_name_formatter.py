#!/usr/bin/env python3

import platform
import sys
import unittest.mock
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from unittest.mock import MagicMock

import praw.models
import pytest

from bdfr.file_name_formatter import FileNameFormatter
from bdfr.resource import Resource
from bdfr.site_downloaders.base_downloader import BaseDownloader
from bdfr.site_downloaders.fallback_downloaders.ytdlp_fallback import YtdlpFallback
from bdfr.site_downloaders.self_post import SelfPost


@pytest.fixture()
def submission() -> MagicMock:
    test = MagicMock()
    test.title = "name"
    test.subreddit.display_name = "randomreddit"
    test.author.name = "person"
    test.id = "12345"
    test.score = 1000
    test.link_flair_text = "test_flair"
    test.created_utc = datetime(2021, 4, 21, 9, 30, 0).timestamp()
    test.__class__ = praw.models.Submission
    return test


@pytest.fixture()
def test_formatter() -> FileNameFormatter:
    out = FileNameFormatter("{TITLE}", "", "ISO")
    return out


def check_valid_windows_path(test_string: str):
    return test_string == FileNameFormatter._format_for_windows(test_string)


def do_test_string_equality(result: Union[Path, str], expected: str) -> bool:
    if platform.system() == "Windows":
        expected = FileNameFormatter._format_for_windows(expected)
    return str(result).endswith(expected)


def do_test_path_equality(result: Path, expected: str) -> bool:
    if platform.system() == "Windows":
        expected = expected.split("/")
        expected = [FileNameFormatter._format_for_windows(part) for part in expected]
        expected = Path(*expected)
    else:
        expected = Path(expected)
    return str(result).endswith(str(expected))  # noqa: FURB123


@pytest.fixture(scope="session")
def reddit_submission(reddit_instance: praw.Reddit) -> praw.models.Submission:
    return reddit_instance.submission(id="w22m5l")


@pytest.mark.parametrize(
    ("test_format_string", "expected"),
    (
        ("{SUBREDDIT}", "randomreddit"),
        ("{REDDITOR}", "person"),
        ("{POSTID}", "12345"),
        ("{UPVOTES}", "1000"),
        ("{FLAIR}", "test_flair"),
        ("{DATE}", "2021-04-21T09:30:00"),
        ("{REDDITOR}_{TITLE}_{POSTID}", "person_name_12345"),
    ),
)
def test_format_name_mock(test_format_string: str, expected: str, submission: MagicMock):
    test_formatter = FileNameFormatter(test_format_string, "", "ISO")
    result = test_formatter._format_name(submission, test_format_string)
    assert do_test_string_equality(result, expected)


@pytest.mark.parametrize(
    ("test_string", "expected"),
    (
        ("", False),
        ("test", False),
        ("{POSTID}", True),
        ("POSTID", False),
        ("{POSTID}_test", True),
        ("test_{TITLE}", True),
        ("TITLE_POSTID", False),
    ),
)
def test_check_format_string_validity(test_string: str, expected: bool):
    result = FileNameFormatter.validate_string(test_string)
    assert result == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    "restriction_scheme",
    (
        "windows",
        "linux",
        "bla",
        None,
    ),
)
@pytest.mark.parametrize(
    ("test_format_string", "expected"),
    (
        ("{SUBREDDIT}", "formula1"),
        ("{REDDITOR}", "Kirsty-Blue"),
        ("{POSTID}", "w22m5l"),
        ("{FLAIR}", "Social Media rall"),
        ("{SUBREDDIT}_{TITLE}", "formula1_George Russel acknowledges the Twitter trend about him"),
        ("{REDDITOR}_{TITLE}_{POSTID}", "Kirsty-Blue_George Russel acknowledges the Twitter trend about him_w22m5l"),
    ),
)
def test_format_name_real(
    test_format_string: str,
    expected: str,
    reddit_submission: praw.models.Submission,
    restriction_scheme: Optional[str],
):
    test_formatter = FileNameFormatter(test_format_string, "", "", restriction_scheme)
    result = test_formatter._format_name(reddit_submission, test_format_string)
    assert do_test_string_equality(result, expected)
    if restriction_scheme == "windows":
        assert check_valid_windows_path(result)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("format_string_directory", "format_string_file", "expected"),
    (
        (
            "{SUBREDDIT}",
            "{POSTID}",
            "test/formula1/w22m5l.png",
        ),
        (
            "{SUBREDDIT}",
            "{TITLE}_{POSTID}",
            "test/formula1/George Russel acknowledges the Twitter trend about him_w22m5l.png",
        ),
        (
            "{SUBREDDIT}",
            "{REDDITOR}_{TITLE}_{POSTID}",
            "test/formula1/Kirsty-Blue_George Russel acknowledges the Twitter trend about him_w22m5l.png",
        ),
    ),
)
def test_format_full(
    format_string_directory: str, format_string_file: str, expected: str, reddit_submission: praw.models.Submission
):
    test_resource = Resource(reddit_submission, "i.reddit.com/blabla.png", lambda: None)
    test_formatter = FileNameFormatter(format_string_file, format_string_directory, "ISO")
    result = test_formatter.format_path(test_resource, Path("test"))
    assert do_test_path_equality(result, expected)


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("format_string_directory", "format_string_file"),
    (
        ("{SUBREDDIT}", "{POSTID}"),
        ("{SUBREDDIT}", "{UPVOTES}"),
        ("{SUBREDDIT}", "{UPVOTES}{POSTID}"),
    ),
)
def test_format_full_conform(
    format_string_directory: str, format_string_file: str, reddit_submission: praw.models.Submission
):
    test_resource = Resource(reddit_submission, "i.reddit.com/blabla.png", lambda: None)
    test_formatter = FileNameFormatter(format_string_file, format_string_directory, "ISO")
    test_formatter.format_path(test_resource, Path("test"))


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("format_string_directory", "format_string_file", "index", "expected"),
    (
        ("{SUBREDDIT}", "{POSTID}", None, "test/formula1/w22m5l.png"),
        ("{SUBREDDIT}", "{POSTID}", 1, "test/formula1/w22m5l_1.png"),
        ("{SUBREDDIT}", "{POSTID}", 2, "test/formula1/w22m5l_2.png"),
        (
            "{SUBREDDIT}",
            "{TITLE}_{POSTID}",
            2,
            "test/formula1/George Russel acknowledges the Twitter trend about him_w22m5l_2.png",
        ),
    ),
)
def test_format_full_with_index_suffix(
    format_string_directory: str,
    format_string_file: str,
    index: Optional[int],
    expected: str,
    reddit_submission: praw.models.Submission,
):
    test_resource = Resource(reddit_submission, "i.reddit.com/blabla.png", lambda: None)
    test_formatter = FileNameFormatter(format_string_file, format_string_directory, "ISO")
    result = test_formatter.format_path(test_resource, Path("test"), index)
    assert do_test_path_equality(result, expected)


def test_format_multiple_resources():
    mocks = []
    for _i in range(1, 5):
        new_mock = MagicMock()
        new_mock.url = "https://example.com/test.png"
        new_mock.extension = ".png"
        new_mock.source_submission.title = "test"
        new_mock.source_submission.__class__ = praw.models.Submission
        mocks.append(new_mock)
    test_formatter = FileNameFormatter("{TITLE}", "", "ISO")
    results = test_formatter.format_resource_paths(mocks, Path())
    results = set([str(res[0].name) for res in results])
    expected = {"test_1.png", "test_2.png", "test_3.png", "test_4.png"}
    assert results == expected


@pytest.mark.parametrize(
    ("test_filename", "test_ending"),
    (
        ("A" * 300, ".png"),
        ("A" * 300, "_1.png"),
        ("a" * 300, "_1000.jpeg"),
        ("😍💕✨" * 100, "_1.png"),
    ),
)
def test_limit_filename_length(test_filename: str, test_ending: str, test_formatter: FileNameFormatter):
    result = test_formatter.limit_file_name_length(test_filename, test_ending, Path())
    assert len(result.name) <= 255
    assert len(result.name.encode("utf-8")) <= 255
    assert len(str(result)) <= FileNameFormatter.find_max_path_length()
    assert isinstance(result, Path)


@pytest.mark.parametrize(
    ("test_filename", "test_ending", "expected_end"),
    (
        ("test_aaaaaa", "_1.png", "test_aaaaaa_1.png"),
        ("test_aataaa", "_1.png", "test_aataaa_1.png"),
        ("test_abcdef", "_1.png", "test_abcdef_1.png"),
        ("test_aaaaaa", ".png", "test_aaaaaa.png"),
        ("test", "_1.png", "test_1.png"),
        ("test_m1hqw6", "_1.png", "test_m1hqw6_1.png"),
        ("A" * 300 + "_bbbccc", ".png", "_bbbccc.png"),
        ("A" * 300 + "_bbbccc", "_1000.jpeg", "_bbbccc_1000.jpeg"),
        ("😍💕✨" * 100 + "_aaa1aa", "_1.png", "_aaa1aa_1.png"),
    ),
)
def test_preserve_id_append_when_shortening(
    test_filename: str, test_ending: str, expected_end: str, test_formatter: FileNameFormatter
):
    result = test_formatter.limit_file_name_length(test_filename, test_ending, Path())
    assert len(result.name) <= 255
    assert len(result.name.encode("utf-8")) <= 255
    assert result.name.endswith(expected_end)
    assert len(str(result)) <= FileNameFormatter.find_max_path_length()


@pytest.mark.skipif(sys.platform == "win32", reason="Test broken on windows github")
def test_shorten_filename_real(submission: MagicMock, tmp_path: Path):
    submission.title = "A" * 500
    submission.author.name = "test"
    submission.subreddit.display_name = "test"
    submission.id = "BBBBBB"
    test_resource = Resource(submission, "www.example.com/empty", lambda: None, ".jpeg")
    test_formatter = FileNameFormatter("{REDDITOR}_{TITLE}_{POSTID}", "{SUBREDDIT}", "ISO")
    result = test_formatter.format_path(test_resource, tmp_path)
    result.parent.mkdir(parents=True)
    result.touch()


@pytest.mark.parametrize(
    ("test_name", "test_ending"),
    (
        ("a", "b"),
        ("a", "_bbbbbb.jpg"),
        ("a" * 20, "_bbbbbb.jpg"),
        ("a" * 50, "_bbbbbb.jpg"),
        ("a" * 500, "_bbbbbb.jpg"),
    ),
)
def test_shorten_path(test_name: str, test_ending: str, tmp_path: Path, test_formatter: FileNameFormatter):
    result = test_formatter.limit_file_name_length(test_name, test_ending, tmp_path)
    assert len(str(result.name)) <= 255
    assert len(str(result.name).encode("UTF-8")) <= 255
    assert len(str(result.name).encode("cp1252")) <= 255
    assert len(str(result)) <= FileNameFormatter.find_max_path_length()


@pytest.mark.parametrize(
    ("test_string", "expected"),
    (
        ("test", "test"),
        ("test😍", "test"),
        ("test.png", "test.png"),
        ("test*", "test"),
        ("test**", "test"),
        ("test?*", "test"),
        ("test_???.png", "test_.png"),
        ("test_???😍.png", "test_.png"),
    ),
)
def test_format_file_name_for_windows(test_string: str, expected: str):
    result = FileNameFormatter._format_for_windows(test_string)
    assert result == expected


@pytest.mark.parametrize(
    ("test_string", "expected"),
    (
        ("test", "test"),
        ("test😍", "test"),
        ("😍", ""),
    ),
)
def test_strip_emojies(test_string: str, expected: str):
    result = FileNameFormatter._strip_emojis(test_string)
    assert result == expected


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("test_submission_id", "expected"),
    (
        (
            "718ifq",
            {
                "title": "Wood Stormtrooper Carving",
                "redditor": "deathakissaway",
            },
        ),
    ),
)
def test_generate_dict_for_submission(test_submission_id: str, expected: dict, reddit_instance: praw.Reddit):
    test_submission = reddit_instance.submission(id=test_submission_id)
    test_formatter = FileNameFormatter("{TITLE}", "", "ISO")
    result = test_formatter._generate_name_dict_from_submission(test_submission)
    assert all([result.get(key) == expected[key] for key in expected.keys()])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("test_comment_id", "expected"),
    (
        (
            "dn8xwh1",
            {
                "title": "Wood Stormtrooper Carving",
                "redditor": "lemonman37",
                "postid": "dn8xwh1",
                "flair": "",
            },
        ),
    ),
)
def test_generate_dict_for_comment(test_comment_id: str, expected: dict, reddit_instance: praw.Reddit):
    test_comment = reddit_instance.comment(id=test_comment_id)
    test_formatter = FileNameFormatter("{TITLE}", "", "ISO")
    result = test_formatter._generate_name_dict_from_comment(test_comment)
    assert all([result.get(key) == expected[key] for key in expected.keys()])


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("test_file_scheme", "test_folder_scheme", "test_comment_id", "expected_name"),
    (
        ("{POSTID}", "", "gsoubde", "gsoubde.json"),
        ("{REDDITOR}_{POSTID}", "", "gsoubde", "DELETED_gsoubde.json"),
    ),
)
def test_format_archive_entry_comment(
    test_file_scheme: str,
    test_folder_scheme: str,
    test_comment_id: str,
    expected_name: str,
    tmp_path: Path,
    reddit_instance: praw.Reddit,
):
    test_comment = reddit_instance.comment(id=test_comment_id)
    test_formatter = FileNameFormatter(test_file_scheme, test_folder_scheme, "ISO")
    test_entry = Resource(test_comment, "", lambda: None, ".json")
    result = test_formatter.format_path(test_entry, tmp_path)
    assert do_test_string_equality(result, expected_name)


@pytest.mark.parametrize(
    ("test_folder_scheme", "expected"),
    (
        ("{REDDITOR}/{SUBREDDIT}", "person/randomreddit"),
        ("{POSTID}/{SUBREDDIT}/{REDDITOR}", "12345/randomreddit/person"),
    ),
)
def test_multilevel_folder_scheme(
    test_folder_scheme: str,
    expected: str,
    tmp_path: Path,
    submission: MagicMock,
):
    test_formatter = FileNameFormatter("{POSTID}", test_folder_scheme, "ISO")
    test_resource = MagicMock()
    test_resource.source_submission = submission
    test_resource.extension = ".png"
    result = test_formatter.format_path(test_resource, tmp_path)
    result = result.relative_to(tmp_path)
    assert do_test_path_equality(result.parent, expected)
    assert len(result.parents) == (len(expected.split("/")) + 1)


@pytest.mark.parametrize(
    ("test_name_string", "expected"),
    (
        ("test", "test"),
        ("😍", "😍"),
        ("test😍", "test😍"),
        ("test😍 ’", "test😍 ’"),  # noqa: RUF001
        ("test😍 \\u2019", "test😍 ’"),  # noqa: RUF001
        ("Using that real good [1\\4]", "Using that real good [1\\4]"),
    ),
)
def test_preserve_emojis(test_name_string: str, expected: str, submission: MagicMock):
    submission.title = test_name_string
    test_formatter = FileNameFormatter("{TITLE}", "", "ISO")
    result = test_formatter._format_name(submission, "{TITLE}")
    assert do_test_string_equality(result, expected)


@pytest.mark.parametrize(
    ("test_string", "expected"),
    (
        ("test \\u2019", "test ’"),  # noqa: RUF001
        ("My cat\\u2019s paws are so cute", "My cat’s paws are so cute"),  # noqa: RUF001
    ),
)
def test_convert_unicode_escapes(test_string: str, expected: str):
    result = FileNameFormatter._convert_unicode_escapes(test_string)
    assert result == expected


@pytest.mark.parametrize(
    ("test_datetime", "expected"),
    (
        (datetime(2020, 1, 1, 8, 0, 0), "2020-01-01T08:00:00"),
        (datetime(2020, 1, 1, 8, 0), "2020-01-01T08:00:00"),
        (datetime(2021, 4, 21, 8, 30, 21), "2021-04-21T08:30:21"),
    ),
)
def test_convert_timestamp(test_datetime: datetime, expected: str):
    test_timestamp = test_datetime.timestamp()
    test_formatter = FileNameFormatter("{POSTID}", "", "ISO")
    result = test_formatter._convert_timestamp(test_timestamp)
    assert result == expected


@pytest.mark.parametrize(
    ("test_time_format", "expected"),
    (
        ("ISO", "2021-05-02T13:33:00"),
        ("%Y_%m", "2021_05"),
        ("%Y-%m-%d", "2021-05-02"),
    ),
)
def test_time_string_formats(test_time_format: str, expected: str):
    test_time = datetime(2021, 5, 2, 13, 33)
    test_formatter = FileNameFormatter("{TITLE}", "", test_time_format)
    result = test_formatter._convert_timestamp(test_time.timestamp())
    assert result == expected


def test_get_max_path_length():
    result = FileNameFormatter.find_max_path_length()
    assert result in (4096, 260, 1024)


def test_windows_max_path(tmp_path: Path):
    with unittest.mock.patch("platform.system", return_value="Windows"):
        with unittest.mock.patch("bdfr.file_name_formatter.FileNameFormatter.find_max_path_length", return_value=260):
            mock = MagicMock()
            mock.max_path = 260
            result = FileNameFormatter.limit_file_name_length(mock, "test" * 100, "_1.png", tmp_path)
            assert len(str(result)) <= 260
            assert len(result.name) <= (260 - len(str(tmp_path)))


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(
    ("test_reddit_id", "test_downloader", "expected_names"),
    (
        ("gphmnr", YtdlpFallback, {"He has a lot to say today.mp4"}),
        ("d0oir2", YtdlpFallback, {"Crunk's finest moment. Welcome to the new subreddit!.mp4"}),
        ("jiecu", SelfPost, {"[deleted by user].txt"}),
    ),
)
def test_name_submission(
    test_reddit_id: str,
    test_downloader: type[BaseDownloader],
    expected_names: set[str],
    reddit_instance: praw.reddit.Reddit,
):
    test_submission = reddit_instance.submission(id=test_reddit_id)
    test_resources = test_downloader(test_submission).find_resources()
    test_formatter = FileNameFormatter("{TITLE}", "", "")
    results = test_formatter.format_resource_paths(test_resources, Path())
    results = set([r[0].name for r in results])
    assert results == expected_names


@pytest.mark.parametrize(
    ("test_filename", "test_ending", "expected_end"),
    (
        ("A" * 300 + ".", "_1.mp4", "A_1.mp4"),
        ("A" * 300 + ".", ".mp4", "A.mp4"),
        ("A" * 300 + ".", "mp4", "A.mp4"),
    ),
)
def test_shortened_file_name_ending(
    test_filename: str, test_ending: str, expected_end: str, test_formatter: FileNameFormatter
):
    result = test_formatter.limit_file_name_length(test_filename, test_ending, Path())
    assert result.name.endswith(expected_end)
    assert len(str(result)) <= FileNameFormatter.find_max_path_length()
