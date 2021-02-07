import json
import os
import pathlib

import requests

from bulkredditdownloader.downloaders.direct import Direct
from bulkredditdownloader.downloaders.downloader_utils import getFile
from bulkredditdownloader.errors import (AlbumNotDownloadedCompletely, ExtensionError, FileAlreadyExistsError, ImageNotFound,
                                         NotADownloadableLinkError, TypeInSkip)
from bulkredditdownloader.utils import GLOBAL, nameCorrector
from bulkredditdownloader.utils import printToFile as print


class Imgur:

    imgur_image_domain = "https://i.imgur.com/"

    def __init__(self, directory: pathlib.Path, post: dict):
        link = post['CONTENTURL']

        if link.endswith(".gifv"):
            link = link.replace(".gifv", ".mp4")
            Direct(directory, {**post, 'CONTENTURL': link})
            return

        self.raw_data = self.getData(link)

        self.directory = directory
        self.post = post

        if self.isAlbum:
            if self.raw_data["album_images"]["count"] != 1:
                self.downloadAlbum(self.raw_data["album_images"])
            else:
                self.download(self.raw_data["album_images"]["images"][0])
        else:
            self.download(self.raw_data)

    def downloadAlbum(self, images: dict):
        folder_name = GLOBAL.config['filename'].format(**self.post)
        folder_dir = self.directory / folder_name

        images_length = images["count"]
        how_many_downloaded = 0
        duplicates = 0

        try:
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir)
        except FileNotFoundError:
            folder_dir = self.directory / self.post['POSTID']
            os.makedirs(folder_dir)

        print(folder_name)

        for i in range(images_length):
            extension = self.validateExtension(images["images"][i]["ext"])
            image_url = self.imgur_image_domain + images["images"][i]["hash"] + extension
            filename = "_".join([str(i + 1),
                                 nameCorrector(images["images"][i]['title']),
                                 images["images"][i]['hash']]) + extension
            short_filename = str(i + 1) + "_" + images["images"][i]['hash']

            print("\n  ({}/{})".format(i + 1, images_length))

            try:
                getFile(filename, short_filename, folder_dir, image_url, indent=2)
                how_many_downloaded += 1
                print()

            except FileAlreadyExistsError:
                print("  The file already exists" + " " * 10, end="\n\n")
                duplicates += 1

            except TypeInSkip:
                print("  Skipping...")
                how_many_downloaded += 1

            except Exception as exception:
                print("\n  Could not get the file")
                print(
                    "  " +
                    "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                        class_name=exception.__class__.__name__,
                        info=str(exception)
                    )
                    + "\n"
                )
                print(GLOBAL.log_stream.getvalue(), no_print=True)

        if duplicates == images_length:
            raise FileAlreadyExistsError
        elif how_many_downloaded + duplicates < images_length:
            raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")

    def download(self, image: dict):
        extension = self.validateExtension(image["ext"])
        image_url = self.imgur_image_domain + image["hash"] + extension

        filename = GLOBAL.config['filename'].format(**self.post) + extension
        short_filename = self.post['POSTID'] + extension

        getFile(filename, short_filename, self.directory, image_url)

    @property
    def isAlbum(self) -> bool:
        return "album_images" in self.raw_data

    @staticmethod
    def getData(link: str) -> dict:
        cookies = {"over18": "1", "postpagebeta": "0"}
        res = requests.get(link, cookies=cookies)
        if res.status_code != 200:
            raise ImageNotFound(f"Server responded with {res.status_code} to {link}")
        page_source = requests.get(link, cookies=cookies).text

        starting_string = "image               : "
        ending_string = "group               :"

        starting_string_lenght = len(starting_string)
        try:
            start_index = page_source.index(starting_string) + starting_string_lenght
            end_index = page_source.index(ending_string, start_index)
        except ValueError:
            raise NotADownloadableLinkError(
                f"Could not read the page source on {link}")

        while page_source[end_index] != "}":
            end_index -= 1
        try:
            data = page_source[start_index:end_index + 2].strip()[:-1]
        except Exception:
            page_source[end_index + 1] = '}'
            data = page_source[start_index:end_index + 3].strip()[:-1]

        return json.loads(data)

    @staticmethod
    def validateExtension(string: str) -> str:
        possible_extensions = [".jpg", ".png", ".mp4", ".gif"]

        for extension in possible_extensions:
            if extension in string:
                return extension
        else:
            raise ExtensionError(f"\"{string}\" is not recognized as a valid extension.")
