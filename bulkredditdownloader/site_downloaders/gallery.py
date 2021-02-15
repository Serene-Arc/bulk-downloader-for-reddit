#!/usr/bin/env python3

import json
import logging

import requests
from praw.models import Submission

from bulkredditdownloader.errors import NotADownloadableLinkError, ResourceNotFound
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Gallery(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)
        link = self.post.url
        self.raw_data = self._get_data(link)

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

        return self._download_album(images)

    @staticmethod
    def _get_data(link: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/67.0.3396.87 Safari/537.36 OPR/54.0.2952.64",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        res = requests.get(link, headers=headers)
        if res.status_code != 200:
            raise ResourceNotFound(f"Server responded with {res.status_code} to {link}")
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

    def _download_album(self, images: dict):
        out = []
        for image_key in images.keys():
            out.append(self._download_resource(images[image_key]['url']))
        return out
