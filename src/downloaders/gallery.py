import os
import json
import urllib
import requests

from src.utils import GLOBAL
from src.utils import printToFile as print
from src.downloaders.downloaderUtils import getFile
from src.errors import FileNotFoundError, FileAlreadyExistsError, AlbumNotDownloadedCompletely, ImageNotFound, NotADownloadableLinkError, TypeInSkip


class gallery:
    def __init__(self, directory, post):

        link = post['CONTENTURL']
        self.rawData = self.getData(link)

        self.directory = directory
        self.post = post

        images = {}
        count = 0
        for model in self.rawData['posts']['models']:
            try:
                for item in self.rawData['posts']['models'][model]['media']['gallery']['items']:
                    try:
                        images[count] = {'id': item['mediaId'], 'url': self.rawData['posts'][
                            'models'][model]['media']['mediaMetadata'][item['mediaId']]['s']['u']}
                        count = count + 1
                    except BaseException:
                        continue
            except BaseException:
                continue

        self.downloadAlbum(images, count)

    @staticmethod
    def getData(link):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        res = requests.get(link, headers=headers)
        if res.status_code != 200:
            raise ImageNotFound(
                f"Server responded with {res.status_code} to {link}")
        pageSource = res.text

        STARTING_STRING = "_r = {"
        ENDING_STRING = "</script>"

        STARTING_STRING_LENGHT = len(STARTING_STRING)
        try:
            startIndex = pageSource.index(
                STARTING_STRING) + STARTING_STRING_LENGHT
            endIndex = pageSource.index(ENDING_STRING, startIndex)
        except ValueError:
            raise NotADownloadableLinkError(
                f"Could not read the page source on {link}")

        data = json.loads(pageSource[startIndex - 1:endIndex + 1].strip()[:-1])
        return data

    def downloadAlbum(self, images, count):
        folderName = GLOBAL.config['filename'].format(**self.post)
        folderDir = self.directory / folderName

        howManyDownloaded = 0
        duplicates = 0

        try:
            if not os.path.exists(folderDir):
                os.makedirs(folderDir)
        except FileNotFoundError:
            folderDir = self.directory / self.post['POSTID']
            os.makedirs(folderDir)

        print(folderName)

        for i in range(count):
            path = urllib.parse.urlparse(images[i]['url']).path
            extension = os.path.splitext(path)[1]

            filename = "_".join([
                str(i + 1), images[i]['id']
            ]) + extension
            shortFilename = str(i + 1) + "_" + images[i]['id']

            print("\n  ({}/{})".format(i + 1, count))

            try:
                getFile(filename, shortFilename, folderDir,
                        images[i]['url'], indent=2)
                howManyDownloaded += 1
                print()

            except FileAlreadyExistsError:
                print("  The file already exists" + " " * 10, end="\n\n")
                duplicates += 1

            except TypeInSkip:
                print("  Skipping...")
                howManyDownloaded += 1

            except Exception as exception:
                print("\n  Could not get the file")
                print(
                    "  " +
                    "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                        class_name=exception.__class__.__name__,
                        info=str(exception)) +
                    "\n")
                print(GLOBAL.log_stream.getvalue(), noPrint=True)

        if duplicates == count:
            raise FileAlreadyExistsError
        if howManyDownloaded + duplicates < count:
            raise AlbumNotDownloadedCompletely(
                "Album Not Downloaded Completely"
            )
