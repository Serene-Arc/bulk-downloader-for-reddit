import io
import sys
from os import makedirs, path
from pathlib import Path

from src.jsonHelper import JsonFile


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
    @staticmethod
    def downloadedPosts(): return []
    printVanilla = print

    log_stream = None


def createLogFile(TITLE):
    """Create a log file with given name
    inside a folder time stampt in its name and
    put given arguments inside \"HEADER\" key
    """

    folderDirectory = GLOBAL.directory / "LOG_FILES" / GLOBAL.RUN_TIME

    logFilename = TITLE.upper() + '.json'

    if not path.exists(folderDirectory):
        makedirs(folderDirectory)

    FILE = JsonFile(folderDirectory / Path(logFilename))
    HEADER = " ".join(sys.argv)
    FILE.add({"HEADER": HEADER})

    return FILE


def printToFile(*args, noPrint=False, **kwargs):
    """Print to both CONSOLE and
    CONSOLE LOG file in a folder time stampt in the name
    """

    folderDirectory = GLOBAL.directory / \
        Path("LOG_FILES") / Path(GLOBAL.RUN_TIME)

    if not noPrint or \
       GLOBAL.arguments.verbose or \
       "file" in kwargs:

        print(*args, **kwargs)

    if not path.exists(folderDirectory):
        makedirs(folderDirectory)

    if "file" not in kwargs:
        with io.open(
            folderDirectory / "CONSOLE_LOG.txt", "a", encoding="utf-8"
        ) as FILE:
            print(*args, file=FILE, **kwargs)


def nameCorrector(string, reference=None):
    """Swap strange characters from given string
    with underscore (_) and shorten it.
    Return the string
    """

    LIMIT = 247

    stringLength = len(string)

    if reference:
        referenceLenght = len(reference)
        totalLenght = referenceLenght
    else:
        totalLenght = stringLength

    if totalLenght > LIMIT:
        limit = LIMIT - referenceLenght
        string = string[:limit - 1]

    string = string.replace(" ", "_")

    if len(string.split('\n')) > 1:
        string = "".join(string.split('\n'))

    BAD_CHARS = ['\\', '/', ':', '*', '?', '"', '<',
                 '>', '|', '#', '.', '@', '“', '’', '\'', '!']
    string = "".join([i if i not in BAD_CHARS else "_" for i in string])

    return string
