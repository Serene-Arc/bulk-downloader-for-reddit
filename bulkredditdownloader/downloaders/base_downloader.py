#!/usr/bin/env python3
# coding=utf-8

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from bulkredditdownloader.errors import DomainInSkip, FailedToDownload, FileAlreadyExistsError, TypeInSkip
from bulkredditdownloader.utils import GLOBAL

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    def __init__(self, directory: Path, post: dict):
        self.directory = directory
        self.post = post

    @abstractmethod
    def download(self):
        raise NotImplementedError

    @staticmethod
    def _create_hash(content: bytes) -> str:
        hash_md5 = hashlib.md5(content)
        return hash_md5.hexdigest()

    @staticmethod
    def _download_resource(filename: Path, folder_dir: Path, image_url: str, indent: int = 0, silent: bool = False):
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
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"),
            ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3"),
            ("Accept-Encoding", "none"),
            ("Accept-Language", "en-US,en;q=0.8"),
            ("Connection", "keep-alive")
        ]

        folder_dir.mkdir(exist_ok=True)

        if "imgur" not in image_url:
            addheaders = headers
        else:
            addheaders = None

        if not silent:
            logger.info(" " * indent + str(folder_dir), " " * indent + str(filename), sep="\n")

        # Loop to attempt download 3 times
        for i in range(3):
            file_path = Path(folder_dir) / filename

            if file_path.is_file():
                raise FileAlreadyExistsError
            else:
                try:
                    download_content = requests.get(image_url, headers=addheaders).content
                except ConnectionResetError:
                    raise FailedToDownload

                file_hash = BaseDownloader._create_hash(download_content)
                if GLOBAL.arguments.no_dupes:
                    if file_hash in GLOBAL.downloadedPosts():
                        raise FileAlreadyExistsError
                GLOBAL.downloadedPosts.add(file_hash)

                with open(file_path, 'wb') as file:
                    file.write(download_content)
                if not silent:
                    logger.info(" " * indent + "Downloaded" + " " * 10)
                return

        raise FailedToDownload

    @staticmethod
    def _get_extension(url: str) -> str:
        pattern = re.compile(r'(\.(jpg|jpeg|png|mp4|webm|gif))')
        if len(results := re.search(pattern, url).groups()) > 1:
            return results[1]
        if "v.redd.it" not in url:
            return '.jpg'
        else:
            return '.mp4'
