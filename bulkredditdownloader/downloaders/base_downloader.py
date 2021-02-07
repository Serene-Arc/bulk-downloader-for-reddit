#!/usr/bin/env python3
# coding=utf-8
import hashlib
import os
import sys
import urllib.request
from abc import ABC
from pathlib import Path

from bulkredditdownloader.errors import DomainInSkip, FailedToDownload, FileAlreadyExistsError, TypeInSkip
from bulkredditdownloader.utils import GLOBAL
from bulkredditdownloader.utils import printToFile as print


class BaseDownloader(ABC):
    def __init__(self, directory: Path, post: dict):
        self.directory = directory
        self.post = post

    @staticmethod
    def createHash(filename: str) -> str:
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def dlProgress(count: int, block_size: int, total_size: int):
        """Function for writing download progress to console """
        download_mbs = int(count * block_size * (10 ** (-6)))
        file_size = int(total_size * (10 ** (-6)))
        sys.stdout.write("{}Mb/{}Mb\r".format(download_mbs, file_size))
        sys.stdout.flush()

    @staticmethod
    def getFile(
            filename: str,
            short_filename: str,
            folder_dir: Path,
            image_url: str,
            indent: int = 0,
            silent: bool = False):
        formats = {
            "videos": [".mp4", ".webm"],
            "images": [".jpg", ".jpeg", ".png", ".bmp"],
            "gifs": [".gif"],
            "self": []
        }

        for file_type in GLOBAL.arguments.skip:
            for extension in formats[file_type]:
                if extension in filename:
                    raise TypeInSkip

        if any(domain in image_url for domain in GLOBAL.arguments.skip_domain):
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

        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)

        opener = urllib.request.build_opener()
        if "imgur" not in image_url:
            opener.addheaders = headers
        urllib.request.install_opener(opener)

        if not silent:
            print(" " * indent + str(folder_dir), " " * indent + str(filename), sep="\n")

        for i in range(3):
            file_dir = Path(folder_dir) / filename
            temp_dir = Path(folder_dir) / (filename + ".tmp")

            if not (os.path.isfile(file_dir)):
                try:
                    urllib.request.urlretrieve(image_url, temp_dir, reporthook=BaseDownloader.dlProgress)

                    file_hash = BaseDownloader.createHash(temp_dir)
                    if GLOBAL.arguments.no_dupes:
                        if file_hash in GLOBAL.downloadedPosts():
                            os.remove(temp_dir)
                            raise FileAlreadyExistsError
                    GLOBAL.downloadedPosts.add(file_hash)

                    os.rename(temp_dir, file_dir)
                    if not silent:
                        print(" " * indent + "Downloaded" + " " * 10)
                    return None
                except ConnectionResetError:
                    raise FailedToDownload
                except FileNotFoundError:
                    filename = short_filename
            else:
                raise FileAlreadyExistsError
        raise FailedToDownload

    @staticmethod
    def getExtension(link: str):
        """Extract file extension from image link. If didn't find any, return '.jpg' """
        image_types = ['jpg', 'png', 'mp4', 'webm', 'gif']
        parsed = link.split('.')
        for fileType in image_types:
            if fileType in parsed:
                return "." + parsed[-1]
        else:
            if "v.redd.it" not in link:
                return '.jpg'
            else:
                return '.mp4'
