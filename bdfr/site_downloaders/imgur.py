#!/usr/bin/env python3

import json
import re
from typing import Optional

import bs4
from praw.models import Submission

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_authenticator import SiteAuthenticator
from bdfr.site_downloaders.base_downloader import BaseDownloader


class Imgur(BaseDownloader):

    def __init__(self, post: Submission):
        super().__init__(post)
        self.raw_data = {}

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        self.raw_data = self._get_data(self.post.url)

        out = []
        if 'album_images' in self.raw_data:
            images = self.raw_data['album_images']
            for image in images['images']:
                out.append(self._compute_image_url(image))
        else:
            out.append(self._compute_image_url(self.raw_data))
        return out

    def _compute_image_url(self, image: dict) -> Resource:
        image_url = 'https://i.imgur.com/' + image['hash'] + self._validate_extension(image['ext'])
        return Resource(self.post, image_url)

    @staticmethod
    def _get_data(link: str) -> dict:
        if re.match(r'.*\.gifv$', link):
            link = link.replace('i.imgur', 'imgur')
            link = link.rstrip('.gifv')

        res = Imgur.retrieve_url(link, cookies={'over18': '1', 'postpagebeta': '0'})

        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        scripts = soup.find_all('script', attrs={'type': 'text/javascript'})
        scripts = [script.string.replace('\n', '') for script in scripts if script.string]

        script_regex = re.compile(r'\s*\(function\(widgetFactory\)\s*{\s*widgetFactory\.mergeConfig\(\'gallery\'')
        chosen_script = list(filter(lambda s: re.search(script_regex, s), scripts))
        if len(chosen_script) != 1:
            raise SiteDownloaderError(f'Could not read page source from {link}')

        chosen_script = chosen_script[0]

        outer_regex = re.compile(r'widgetFactory\.mergeConfig\(\'gallery\', ({.*})\);')
        inner_regex = re.compile(r'image\s*:(.*),\s*group')
        try:
            image_dict = re.search(outer_regex, chosen_script).group(1)
            image_dict = re.search(inner_regex, image_dict).group(1)
        except AttributeError:
            raise SiteDownloaderError(f'Could not find image dictionary in page source')

        try:
            image_dict = json.loads(image_dict)
        except json.JSONDecodeError as e:
            raise SiteDownloaderError(f'Could not parse received dict as JSON: {e}')

        return image_dict

    @staticmethod
    def _validate_extension(extension_suffix: str) -> str:
        possible_extensions = ('.jpg', '.png', '.mp4', '.gif')
        selection = [ext for ext in possible_extensions if ext == extension_suffix]
        if len(selection) == 1:
            return selection[0]
        else:
            raise SiteDownloaderError(f'"{extension_suffix}" is not recognized as a valid extension for Imgur')
