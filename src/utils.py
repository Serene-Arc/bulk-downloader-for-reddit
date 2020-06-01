import io
import json
import sys
from os import makedirs, path, remove
from pathlib import Path

from src.jsonHelper import JsonFile
from src.errors import FileNotFoundError

class GLOBAL:
    """Declare global variables"""

    RUN_TIME = ""
    config = {'imgur_client_id':None, 'imgur_client_secret': None}
    arguments = None
    directory = None
    defaultConfigDirectory = Path.home() / "Bulk Downloader for Reddit"
    configDirectory = ""
    reddit_client_id = "U-6gk4ZCh3IeNQ"
    reddit_client_secret = "7CZHY6AmKweZME5s50SfDGylaPg"
    hashList = set()
    downloadedPosts = lambda: []
    printVanilla = print

def createLogFile(TITLE):
    """Create a log file with given name
    inside a folder time stampt in its name and
    put given arguments inside \"HEADER\" key
    """

    folderDirectory = GLOBAL.directory / "LOG_FILES" / GLOBAL.RUN_TIME   

    logFilename = TITLE.upper()+'.json'

    if not path.exists(folderDirectory):
        makedirs(folderDirectory)

    FILE = JsonFile(folderDirectory / Path(logFilename))
    HEADER = " ".join(sys.argv)
    FILE.add({"HEADER":HEADER})

    return FILE

def printToFile(*args, noPrint=False,**kwargs):
    """Print to both CONSOLE and 
    CONSOLE LOG file in a folder time stampt in the name
    """
    
    folderDirectory = GLOBAL.directory / Path("LOG_FILES") / Path(GLOBAL.RUN_TIME)

    if not noPrint or \
       GLOBAL.arguments.verbose or \
       "file" in kwargs:
       
       print(*args,**kwargs)

    if not path.exists(folderDirectory):
        makedirs(folderDirectory)
    
    if not "file" in kwargs:
        with io.open(
            folderDirectory / "CONSOLE_LOG.txt","a",encoding="utf-8"
        ) as FILE:
            print(*args, file=FILE, **kwargs) 

def nameCorrector(string):
    """Swap strange characters from given string 
    with underscore (_) and shorten it.
    Return the string
    """

    stringLenght = len(string)
    if stringLenght > 200:
        string = string[:200]
    stringLenght = len(string)
    spacesRemoved = []

    for b in range(stringLenght):
        if string[b] == " ":
            spacesRemoved.append("_")
        else:
            spacesRemoved.append(string[b])
    
    string = ''.join(spacesRemoved)
    
    if len(string.split('\n')) > 1:
        string = "".join(string.split('\n'))
    
    BAD_CHARS = ['\\','/',':','*','?','"','<','>','|','#']
    
    if any(x in string for x in BAD_CHARS):
        for char in string:
            if char in BAD_CHARS:
                string = string.replace(char,"_")

    return string