#!/usr/bin/env python3

import logging
import os
import pathlib
import subprocess
import tempfile

import requests
from praw.models import Submission

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class VReddit(BaseDownloader):
    def __init__(self, post: Submission):
        super().__init__(post)

    def download(self):
        try:
            fnull = open(os.devnull, 'w')
            subprocess.call("ffmpeg", stdout=fnull, stderr=subprocess.STDOUT)
        except subprocess.SubprocessError:
            return self._download_resource(self.post.url)
        else:
            video_url = self.post.url
            audio_url = video_url[:video_url.rfind('/')] + '/DASH_audio.mp4'

            with tempfile.TemporaryDirectory() as temp_dir:
                video = requests.get(video_url).content
                audio = requests.get(audio_url).content
                with open(temp_dir / 'video', 'wb')as file:
                    file.write(video)
                with open(temp_dir / 'audio', 'wb') as file:
                    file.write(audio)
                self._merge_audio(temp_dir)
                with open(temp_dir / 'output.mp4', 'rb') as file:
                    content = file.read()
            return Resource(self.post, self.post.url, content)

    @staticmethod
    def _merge_audio(working_directory: pathlib.Path):
        input_video = working_directory / 'video'
        input_audio = working_directory / 'audio'

        fnull = open(os.devnull, 'w')
        cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(
            input_audio, input_video, str(working_directory / 'output.mp4'))
        subprocess.call(cmd.split(), stdout=fnull, stderr=subprocess.STDOUT)
