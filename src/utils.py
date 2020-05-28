import io
import json
import sys
import time
from os import makedirs, path, remove
from pathlib import Path

from src.errors import FileNotFoundError

class GLOBAL:
    """Declare global variables"""

    RUN_TIME = 0
    config = {'imgur_client_id':None, 'imgur_client_secret': None}
    arguments = None
    directory = None
    defaultConfigDirectory = Path.home() / "Bulk Downloader for Reddit"
    configDirectory = ""
    reddit_client_id = "BSyphDdxYZAgVQ"
    reddit_client_secret = "bfqNJaRh8NMh-9eAr-t4TRz-Blk"
    printVanilla = print

class jsonFile:
    """ Write and read JSON files

    Use add(self,toBeAdded) to add to files

    Use delete(self,*deletedKeys) to delete keys
    """
    
    FILEDIR = ""

    def __init__(self,FILEDIR):
        self.FILEDIR = FILEDIR
        if not path.exists(self.FILEDIR):
            self.__writeToFile({},create=True)

    def read(self):
            with open(self.FILEDIR, 'r') as f:
                return json.load(f)

    def add(self,toBeAdded):
        """Takes a dictionary and merges it with json file.
        It uses new key's value if a key already exists.
        Returns the new content as a dictionary.
        """

        data = self.read()
        data = {**data, **toBeAdded}
        self.__writeToFile(data)
        return self.read()

    def delete(self,*deleteKeys):
        """Delete given keys from JSON file.
        Returns the new content as a dictionary.
        """

        data = self.read()
        for deleteKey in deleteKeys:
            if deleteKey in data:
                del data[deleteKey]
                found = True
        if not found:
            return False
        self.__writeToFile(data)

    def __writeToFile(self,content,create=False):
        if not create:
            remove(self.FILEDIR)
        with open(self.FILEDIR, 'w') as f:
            json.dump(content, f, indent=4)

def createLogFile(TITLE):
    """Create a log file with given name
    inside a folder time stampt in its name and
    put given arguments inside \"HEADER\" key
    """

    folderDirectory = GLOBAL.directory / "LOG_FILES" / \
                      str(time.strftime(
                          "%d-%m-%Y_%H-%M-%S",time.localtime(GLOBAL.RUN_TIME)
                      ))
    logFilename = TITLE.upper()+'.json'

    if not path.exists(folderDirectory):
        makedirs(folderDirectory)

    FILE = jsonFile(folderDirectory / Path(logFilename))
    HEADER = " ".join(sys.argv)
    FILE.add({"HEADER":HEADER})

    return FILE

def printToFile(*args, noPrint=False,**kwargs):
    """Print to both CONSOLE and 
    CONSOLE LOG file in a folder time stampt in the name
    """
    
    TIME = str(time.strftime("%d-%m-%Y_%H-%M-%S",
                             time.localtime(GLOBAL.RUN_TIME)))
    folderDirectory = GLOBAL.directory / "LOG_FILES" / TIME

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
    correctedString = []
    
    if len(string.split('\n')) > 1:
        string = "".join(string.split('\n'))
    
    BAD_CHARS = ['\\','/',':','*','?','"','<','>','|','.','#']
    
    if any(x in string for x in BAD_CHARS):
        for char in string:
            if char in BAD_CHARS:
                string = string.replace(char,"_")

    return string