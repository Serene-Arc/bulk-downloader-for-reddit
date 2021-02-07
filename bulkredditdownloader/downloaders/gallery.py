import json
import os
import urllib

import requests
import pathlib

from bulkredditdownloader.downloaders.downloader_utils import getFile
from bulkredditdownloader.errors import (AlbumNotDownloadedCompletely, FileAlreadyExistsError, ImageNotFound, NotADownloadableLinkError,
                                         TypeInSkip)
from bulkredditdownloader.utils import GLOBAL
from bulkredditdownloader.utils import printToFile as print


class Gallery:
    def __init__(self, directory: pathlib.Path, post):
        link = post['CONTENTURL']
        self.raw_data = self.getData(link)

        self.directory = directory
        self.post = post

        images = {}
        count = 0
        for model in self.raw_data['posts']['models']:
            try:
                for item in self.raw_data['posts']['models'][model]['media']['gallery']['items']:
                    try:
                        images[count] = {'id': item['mediaId'], 'url': self.raw_data['posts']
                                         ['models'][model]['media']['mediaMetadata'][item['mediaId']]['s']['u']}
                        count += 1
                    except Exception:
                        continue
            except Exception:
                continue

        self.downloadAlbum(images, count)

    @staticmethod
    def getData(link: str) -> dict:
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

    def downloadAlbum(self, images: dict, count: int):
        folder_name = GLOBAL.config['filename'].format(**self.post)
        folder_dir = self.directory / folder_name

        how_many_downloaded = 0
        duplicates = 0

        try:
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir)
        except FileNotFoundError:
            folder_dir = self.directory / self.post['POSTID']
            os.makedirs(folder_dir)

        print(folder_name)

        for i in range(count):
            path = urllib.parse.urlparse(images[i]['url']).path
            extension = os.path.splitext(path)[1]

            filename = "_".join([str(i + 1), images[i]['id']]) + extension
            short_filename = str(i + 1) + "_" + images[i]['id']

            print("\n  ({}/{})".format(i + 1, count))

            try:
                getFile(filename, short_filename, folder_dir, images[i]['url'], indent=2)
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
                print("  " + "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                    class_name=exception.__class__.__name__, info=str(exception)) + "\n"
                )
                print(GLOBAL.log_stream.getvalue(), no_print=True)

        if duplicates == count:
            raise FileAlreadyExistsError
        elif how_many_downloaded + duplicates < count:
            raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")
