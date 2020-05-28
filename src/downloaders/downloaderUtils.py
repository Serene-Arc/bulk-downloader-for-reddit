import sys
import os
from urllib.error import HTTPError
import urllib.request

from src.errors import FileAlreadyExistsError, FileNameTooLong

def dlProgress(count, blockSize, totalSize):
    """Function for writing download progress to console
    """

    downloadedMbs = int(count*blockSize*(10**(-6)))
    fileSize = int(totalSize*(10**(-6)))
    sys.stdout.write("{}Mb/{}Mb\r".format(downloadedMbs,fileSize))
    sys.stdout.flush()

def getExtension(link):
    """Extract file extension from image link.
    If didn't find any, return '.jpg'
    """

    imageTypes = ['jpg','png','mp4','webm','gif']
    parsed = link.split('.')
    for fileType in imageTypes:
        if fileType in parsed:
            return "."+parsed[-1]
    else:
        if not "v.redd.it" in link:
            return '.jpg'
        else:
            return '.mp4'

def getFile(fileDir,tempDir,imageURL,indent=0):
    """Downloads given file to given directory.

    fileDir -- Full file directory
    tempDir -- Full file directory with the extension of '.tmp'
    imageURL -- URL to the file to be downloaded

    redditID -- Post's reddit id if renaming the file is necessary.
                As too long file names seem not working.
    """

    headers = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 "\
            "Safari/537.36 OPR/54.0.2952.64"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;" \
            "q=0.9,image/webp,image/apng,*/*;q=0.8"),
        ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3"),
        ("Accept-Encoding", "none"),
        ("Accept-Language", "en-US,en;q=0.8"),
        ("Connection", "keep-alive")
    ]

    opener = urllib.request.build_opener()
    if not "imgur" in imageURL:
        opener.addheaders = headers
    urllib.request.install_opener(opener)

    if not (os.path.isfile(fileDir)):
        for i in range(3):
            try:
                urllib.request.urlretrieve(imageURL,
                                           tempDir,
                                           reporthook=dlProgress)
                os.rename(tempDir,fileDir)
            except ConnectionResetError as exception:
                print(" "*indent + str(exception))
                print(" "*indent + "Trying again\n")
            except FileNotFoundError:
                raise FileNameTooLong
            else:
                print(" "*indent+"Downloaded"+" "*10)
                break
    else:
        raise FileAlreadyExistsError