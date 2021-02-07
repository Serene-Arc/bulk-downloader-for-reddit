#!/usr/bin/env python3

import json
import pathlib
import logging

import requests

from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.site_downloaders.direct import Direct
from bulkredditdownloader.errors import (AlbumNotDownloadedCompletely, ExtensionError, FileAlreadyExistsError,
                                         ImageNotFound, NotADownloadableLinkError, TypeInSkip)
from bulkredditdownloader.utils import GLOBAL, nameCorrector

logger = logging.getLogger(__name__)


class Imgur(BaseDownloader):

    imgur_image_domain = "https://i.imgur.com/"

    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.raw_data = {}
        self.download()

    def download(self):
        link = self.post['CONTENTURL']

        if link.endswith(".gifv"):
            link = link.replace(".gifv", ".mp4")
            Direct(self.directory, {**self.post, 'CONTENTURL': link})
            return

        self.raw_data = self._get_data(link)

        if self._is_album:
            if self.raw_data["album_images"]["count"] != 1:
                self._download_album(self.raw_data["album_images"])
            else:
                self._download_image(self.raw_data["album_images"]["images"][0])
        else:
            self._download_image(self.raw_data)

    def _download_album(self, images: dict):
        folder_name = GLOBAL.config['filename'].format(**self.post)
        folder_dir = self.directory / folder_name

        images_length = images["count"]
        how_many_downloaded = 0
        duplicates = 0

        folder_dir.mkdir(exist_ok=True)
        logger.info(folder_name)

        for i in range(images_length):
            extension = self._validate_extension(images["images"][i]["ext"])
            image_url = self.imgur_image_domain + images["images"][i]["hash"] + extension
            filename = pathlib.Path("_".join([str(i + 1),
                                              nameCorrector(images["images"][i]['title']),
                                              images["images"][i]['hash']]) + extension)

            logger.info("\n  ({}/{})".format(i + 1, images_length))

            try:
                self._download_resource(filename, folder_dir, image_url, indent=2)
                how_many_downloaded += 1

            except FileAlreadyExistsError:
                logger.info("  The file already exists" + " " * 10, end="\n\n")
                duplicates += 1

            except TypeInSkip:
                logger.info("  Skipping...")
                how_many_downloaded += 1

            except Exception as exception:
                logger.info("\n  Could not get the file")
                logger.info(
                    "  "
                    + "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                        class_name=exception.__class__.__name__,
                        info=str(exception)
                    )
                    + "\n"
                )
                logger.info(GLOBAL.log_stream.getvalue(), no_print=True)

        if duplicates == images_length:
            raise FileAlreadyExistsError
        elif how_many_downloaded + duplicates < images_length:
            raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")

    def _download_image(self, image: dict):
        extension = self._validate_extension(image["ext"])
        image_url = self.imgur_image_domain + image["hash"] + extension

        filename = GLOBAL.config['filename'].format(**self.post) + extension

        self._download_resource(filename, self.directory, image_url)

    def _is_album(self) -> bool:
        return "album_images" in self.raw_data

    @staticmethod
    def _get_data(link: str) -> dict:
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
        except IndexError:
            page_source[end_index + 1] = '}'
            data = page_source[start_index:end_index + 3].strip()[:-1]

        return json.loads(data)

    @staticmethod
    def _validate_extension(extension_suffix: str) -> str:
        possible_extensions = [".jpg", ".png", ".mp4", ".gif"]

        for extension in possible_extensions:
            if extension in extension_suffix:
                return extension
        else:
            raise ExtensionError(f"\"{extension_suffix}\" is not recognized as a valid extension.")
