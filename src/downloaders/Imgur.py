import json
import os
import requests

from src.utils import GLOBAL, nameCorrector
from src.utils import printToFile as print
from src.downloaders.Direct import Direct
from src.downloaders.downloaderUtils import getFile
from src.errors import FileNotFoundError, FileAlreadyExistsError, AlbumNotDownloadedCompletely, ImageNotFound, ExtensionError, NotADownloadableLinkError, TypeInSkip


class Imgur:

    IMGUR_IMAGE_DOMAIN = "https://i.imgur.com/"

    def __init__(self, directory, post):

        link = post['CONTENTURL']

        if link.endswith(".gifv"):
            link = link.replace(".gifv", ".mp4")
            Direct(directory, {**post, 'CONTENTURL': link})
            return None

        self.rawData = self.getData(link)

        self.directory = directory
        self.post = post

        if self.isAlbum:
            if self.rawData["album_images"]["count"] != 1:
                self.downloadAlbum(self.rawData["album_images"])
            else:
                self.download(self.rawData["album_images"]["images"][0])
        else:
            self.download(self.rawData)

    def downloadAlbum(self, images):
        folderName = GLOBAL.config['filename'].format(**self.post)
        folderDir = self.directory / folderName

        imagesLenght = images["count"]
        howManyDownloaded = 0
        duplicates = 0

        try:
            if not os.path.exists(folderDir):
                os.makedirs(folderDir)
        except FileNotFoundError:
            folderDir = self.directory / self.post['POSTID']
            os.makedirs(folderDir)

        print(folderName)

        for i in range(imagesLenght):

            extension = self.validateExtension(images["images"][i]["ext"])

            imageURL = self.IMGUR_IMAGE_DOMAIN + \
                images["images"][i]["hash"] + extension

            filename = "_".join([str(i + 1),
                                 nameCorrector(images["images"][i]['title']),
                                 images["images"][i]['hash']]) + extension
            shortFilename = str(i + 1) + "_" + images["images"][i]['hash']

            print("\n  ({}/{})".format(i + 1, imagesLenght))

            try:
                getFile(filename, shortFilename, folderDir, imageURL, indent=2)
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

        if duplicates == imagesLenght:
            raise FileAlreadyExistsError
        if howManyDownloaded + duplicates < imagesLenght:
            raise AlbumNotDownloadedCompletely(
                "Album Not Downloaded Completely"
            )

    def download(self, image):
        extension = self.validateExtension(image["ext"])
        imageURL = self.IMGUR_IMAGE_DOMAIN + image["hash"] + extension

        filename = GLOBAL.config['filename'].format(**self.post) + extension
        shortFilename = self.post['POSTID'] + extension

        getFile(filename, shortFilename, self.directory, imageURL)

    @property
    def isAlbum(self):
        return "album_images" in self.rawData

    @staticmethod
    def getData(link):

        cookies = {"over18": "1", "postpagebeta": "0"}
        res = requests.get(link, cookies=cookies)
        if res.status_code != 200:
            raise ImageNotFound(
                f"Server responded with {res.status_code} to {link}")
        pageSource = requests.get(link, cookies=cookies).text

        STARTING_STRING = "image               : "
        ENDING_STRING = "group               :"

        STARTING_STRING_LENGHT = len(STARTING_STRING)
        try:
            startIndex = pageSource.index(
                STARTING_STRING) + STARTING_STRING_LENGHT
            endIndex = pageSource.index(ENDING_STRING, startIndex)
        except ValueError:
            raise NotADownloadableLinkError(
                f"Could not read the page source on {link}")

        while pageSource[endIndex] != "}":
            endIndex = endIndex - 1
        try:
            data = pageSource[startIndex:endIndex + 2].strip()[:-1]
        except BaseException:
            pageSource[endIndex + 1] = '}'
            data = pageSource[startIndex:endIndex + 3].strip()[:-1]

        return json.loads(data)

    @staticmethod
    def validateExtension(string):
        POSSIBLE_EXTENSIONS = [".jpg", ".png", ".mp4", ".gif"]

        for extension in POSSIBLE_EXTENSIONS:
            if extension in string:
                return extension

        raise ExtensionError(
            f"\"{string}\" is not recognized as a valid extension.")
