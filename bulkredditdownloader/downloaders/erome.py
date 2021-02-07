#!/usr/bin/env python3

import logging
import pathlib
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.errors import AlbumNotDownloadedCompletely, FileAlreadyExistsError, NotADownloadableLinkError
from bulkredditdownloader.utils import GLOBAL

logger = logging.getLogger(__name__)


class Erome(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.download()

    def download(self):
        try:
            images = self._get_links(self.post['CONTENTURL'])
        except urllib.error.HTTPError:
            raise NotADownloadableLinkError("Not a downloadable link")

        images_length = len(images)
        how_many_downloaded = len(images)
        duplicates = 0

        if images_length == 1:
            """Filenames are declared here"""
            filename = GLOBAL.config['filename'].format(**self.post) + self.post["EXTENSION"]

            image = images[0]
            if not re.match(r'https?://.*', image):
                image = "https://" + image

            self._download_resource(filename, self.directory, image)

        else:
            filename = GLOBAL.config['filename'].format(**self.post)
            logger.info(filename)

            folder_dir = self.directory / filename

            folder_dir.mkdir(exist_ok=True)

            for i, image in enumerate(images):
                extension = self._get_extension(image)
                filename = str(i + 1) + extension

                if not re.match(r'https?://.*', image):
                    image = "https://" + image

                logger.info("  ({}/{})".format(i + 1, images_length))
                logger.info("  {}".format(filename))

                try:
                    self._download_resource(pathlib.Path(filename), folder_dir, image, indent=2)
                except FileAlreadyExistsError:
                    logger.info("  The file already exists" + " " * 10, end="\n\n")
                    duplicates += 1
                    how_many_downloaded -= 1

                except Exception as exception:
                    # raise exception
                    logger.error("\n  Could not get the file")
                    logger.error(
                        "  "
                        + "{class_name}: {info}".format(class_name=exception.__class__.__name__, info=str(exception))
                        + "\n"
                    )
                    how_many_downloaded -= 1

            if duplicates == images_length:
                raise FileAlreadyExistsError
            elif how_many_downloaded + duplicates < images_length:
                raise AlbumNotDownloadedCompletely("Album Not Downloaded Completely")

    @staticmethod
    def _get_links(url: str) -> list[str]:
        content = []
        line_number = None

        # TODO: move to bs4 and requests
        class EromeParser(HTMLParser):
            tag = None

            def handle_starttag(self, tag, attrs):
                self.tag = {tag: {attr[0]: attr[1] for attr in attrs}}

        page_source = (urllib.request.urlopen(url).read().decode().split('\n'))

        """ FIND WHERE ALBUM STARTS IN ORDER NOT TO GET WRONG LINKS"""
        for i in range(len(page_source)):
            obj = EromeParser()
            obj.feed(page_source[i])
            tag = obj.tag

            if tag is not None:
                if "div" in tag:
                    if "id" in tag["div"]:
                        if tag["div"]["id"] == "album":
                            line_number = i
                            break

        for line in page_source[line_number:]:
            obj = EromeParser()
            obj.feed(line)
            tag = obj.tag
            if tag is not None:
                if "img" in tag:
                    if "class" in tag["img"]:
                        if tag["img"]["class"] == "img-front":
                            content.append(tag["img"]["src"])
                elif "source" in tag:
                    content.append(tag["source"]["src"])

        return [link for link in content if link.endswith("_480p.mp4") or not link.endswith(".mp4")]
