import io
import sys
from os import makedirs, path
from pathlib import Path
from typing import Optional

from bulkredditdownloader.jsonHelper import JsonFile


class GLOBAL:
    """Declare global variables"""
    RUN_TIME = ""
    config = {'imgur_client_id': None, 'imgur_client_secret': None}
    arguments = None
    directory = None
    defaultConfigDirectory = Path.home() / "Bulk Downloader for Reddit"
    configDirectory = ""
    reddit_client_id = "U-6gk4ZCh3IeNQ"
    reddit_client_secret = "7CZHY6AmKweZME5s50SfDGylaPg"
    printVanilla = print
    log_stream = None

    @staticmethod
    def downloadedPosts() -> list:
        return []


def createLogFile(title: str) -> JsonFile:
    """Create a log file with given name
    inside a folder time stampt in its name and
    put given arguments inside \"HEADER\" key
    """
    folder_directory = GLOBAL.directory / "LOG_FILES" / GLOBAL.RUN_TIME

    log_filename = title.upper() + '.json'

    if not path.exists(folder_directory):
        makedirs(folder_directory)

    file = JsonFile(folder_directory / Path(log_filename))
    header = " ".join(sys.argv)
    file.add({"HEADER": header})

    return file


def printToFile(*args, no_print=False, **kwargs):
    """Print to both CONSOLE and
    CONSOLE LOG file in a folder time stampt in the name
    """
    folder_directory = GLOBAL.directory / Path("LOG_FILES") / Path(GLOBAL.RUN_TIME)

    if not no_print or GLOBAL.arguments.verbose or "file" in kwargs:
        print(*args, **kwargs)

    if not path.exists(folder_directory):
        makedirs(folder_directory)

    if "file" not in kwargs:
        with io.open(folder_directory / "CONSOLE_LOG.txt", "a", encoding="utf-8") as FILE:
            print(*args, file=FILE, **kwargs)


def nameCorrector(string: str, reference: Optional[str] = None) -> str:
    """Swap strange characters from given string
    with underscore (_) and shorten it.
    Return the string
    """
    limit = 247
    string_length = len(string)

    if reference:
        reference_length = len(reference)
        total_lenght = reference_length
    else:
        total_lenght = string_length

    if total_lenght > limit:
        limit -= reference_length
        string = string[:limit - 1]

    string = string.replace(" ", "_")

    if len(string.split('\n')) > 1:
        string = "".join(string.split('\n'))

    bad_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '#', '.', '@', '“', '’', '\'', '!']
    string = "".join([i if i not in bad_chars else "_" for i in string])

    return string
