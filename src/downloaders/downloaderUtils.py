import sys
import os
import urllib.request
from pathlib import Path
import hashlib

from src.utils import GLOBAL
from src.utils import printToFile as print
from src.errors import FileAlreadyExistsError, FailedToDownload, TypeInSkip, DomainInSkip


def dlProgress(count, blockSize, totalSize):
    """Function for writing download progress to console
    """

    downloadedMbs = int(count * blockSize * (10**(-6)))
    fileSize = int(totalSize * (10**(-6)))
    sys.stdout.write("{}Mb/{}Mb\r".format(downloadedMbs, fileSize))
    sys.stdout.flush()


def getExtension(link):
    """Extract file extension from image link.
    If didn't find any, return '.jpg'
    """

    imageTypes = ['jpg', 'png', 'mp4', 'webm', 'gif']
    parsed = link.split('.')
    for fileType in imageTypes:
        if fileType in parsed:
            return "." + parsed[-1]

    if "v.redd.it" not in link:
        return '.jpg'
    return '.mp4'


def getFile(
        filename,
        shortFilename,
        folderDir,
        imageURL,
        indent=0,
        silent=False):

    FORMATS = {
        "videos": [".mp4", ".webm"],
        "images": [".jpg", ".jpeg", ".png", ".bmp"],
        "gifs": [".gif"],
        "self": []
    }

    for type in GLOBAL.arguments.skip:
        for extension in FORMATS[type]:
            if extension in filename:
                raise TypeInSkip

    if any(domain in imageURL for domain in GLOBAL.arguments.skip_domain):
        raise DomainInSkip

    headers = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 "
            "Safari/537.36 OPR/54.0.2952.64"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,image/apng,*/*;q=0.8"),
        ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3"),
        ("Accept-Encoding", "none"),
        ("Accept-Language", "en-US,en;q=0.8"),
        ("Connection", "keep-alive")
    ]

    if not os.path.exists(folderDir):
        os.makedirs(folderDir)

    opener = urllib.request.build_opener()
    if "imgur" not in imageURL:
        opener.addheaders = headers
    urllib.request.install_opener(opener)

    if not silent:
        print(" " * indent + str(folderDir),
              " " * indent + str(filename),
              sep="\n")

    for i in range(3):
        fileDir = Path(folderDir) / filename
        tempDir = Path(folderDir) / (filename + ".tmp")

        if not (os.path.isfile(fileDir)):
            try:
                urllib.request.urlretrieve(imageURL,
                                           tempDir,
                                           reporthook=dlProgress)

                fileHash = createHash(tempDir)
                if GLOBAL.arguments.no_dupes:
                    if fileHash in GLOBAL.downloadedPosts():
                        os.remove(tempDir)
                        raise FileAlreadyExistsError
                GLOBAL.downloadedPosts.add(fileHash)

                os.rename(tempDir, fileDir)
                if not silent:
                    print(" " * indent + "Downloaded" + " " * 10)
                return None
            except ConnectionResetError:
                raise FailedToDownload
            except FileNotFoundError:
                filename = shortFilename
        else:
            raise FileAlreadyExistsError
    raise FailedToDownload


def createHash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
