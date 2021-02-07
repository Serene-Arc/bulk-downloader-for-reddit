#!/usr/bin/env python3

import json
import pathlib
import logging
import urllib.parse

import requests

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.errors import (AlbumNotDownloadedCompletely, FileAlreadyExistsError, ImageNotFound,
                                         NotADownloadableLinkError, TypeInSkip)
from bulkredditdownloader.utils import GLOBAL

logger = logging.getLogger(__name__)


class Gallery(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post):
        super().__init__(directory, post)
        link = self.post['CONTENTURL']
        self.raw_data = self._get_data(link)
        self.download()

    def download(self):
        images = {}
        count = 0
        for model in self.raw_data['posts']['models']:
            try:
                for item in self.raw_data['posts']['models'][model]['media']['gallery']['items']:
                    try:
                        images[count] = {'id': item['mediaId'], 'url': self.raw_data['posts']
                                         ['models'][model]['media']['mediaMetadata'][item['mediaId']]['s']['u']}
                        count += 1
                    except KeyError:
                        continue
            except KeyError:
                continue

        self._download_album(images, count)

    @staticmethod
    def _get_data(link: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        res = requests.get(link, headers=headers)
        if res.status_code != 200:
            raise ImageNotFound(f"Server responded with {res.status_code} to {link}")
        page_source = res.text

        starting_string = "_r = {"
        ending_string = "</script>"

        starting_string_lenght = len(starting_string)
        try:
            start_index = page_source.index(starting_string) + starting_string_lenght
            end_index = page_source.index(ending_string, start_index)
        except ValueError:
            raise NotADownloadableLinkError(f"Could not read the page source on {link}")

        data = json.loads(page_source[start_index - 1:end_index + 1].strip()[:-1])
        return data

    def _download_album(self, images: dict, count: int):
        folder_name = GLOBAL.config['filename'].format(**self.post)
        folder_dir = self.directory / folder_name

        how_many_downloaded = 0
        duplicates = 0

        folder_dir.mkdir(exist_ok=True)
        logger.info(folder_name)

        for i, image in enumerate(images):
            path = urllib.parse.urlparse(image['url']).path
            extension = pathlib.Path(path).suffix

            filename = pathlib.Path("_".join([str(i + 1), image['id']]) + extension)

            logger.info("\n  ({}/{})".format(i + 1, count))

            try:
                self._download_resource(filename, folder_dir, image['url'], indent=2)
                how_many_downloaded += 1

            except FileAlreadyExistsError:
                logger.info("  The file already exists" + " " * 10, end="\n\n")
                duplicates += 1

            except TypeInSkip:
                logger.info("  Skipping...")
                how_many_downloaded += 1

            except Exception as exception:
                logger.info("\n  Could not get the file")
                logger.info("  " + "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                    class_name=exception.__class__.__name__, info=str(exception)) + "\n"
                )
                logger.info(GLOBAL.log_stream.getvalue(), no_print=True)

        if duplicates == count:
            raise FileAlreadyExistsError
        elif how_many_downloaded + duplicates < count:
            raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")
