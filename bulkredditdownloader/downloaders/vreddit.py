#!/usr/bin/env python3

import logging
import os
import pathlib
import subprocess

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.utils import GLOBAL

logger = logging.getLogger(__name__)


class VReddit(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        self.download()

    def download(self):
        extension = ".mp4"
        self.directory.mkdir(exist_ok=True)

        filename = GLOBAL.config['filename'].format(**self.post) + extension

        try:
            fnull = open(os.devnull, 'w')
            subprocess.call("ffmpeg", stdout=fnull, stderr=subprocess.STDOUT)
        except Exception:
            self._download_resource(filename, self.directory, self.post['CONTENTURL'])
            logger.info("FFMPEG library not found, skipping merging video and audio")
        else:
            video_name = self.post['POSTID'] + "_video"
            video_url = self.post['CONTENTURL']
            audio_name = self.post['POSTID'] + "_audio"
            audio_url = video_url[:video_url.rfind('/')] + '/DASH_audio.mp4'

            logger.info(self.directory, filename, sep="\n")

            self._download_resource(video_name, self.directory, video_url, silent=True)
            self._download_resource(audio_name, self.directory, audio_url, silent=True)
            try:
                self._merge_audio(video_name, audio_name, filename, self.directory)
            except KeyboardInterrupt:
                (self.directory / filename).unlink()
                (self.directory / audio_name).unlink()
                (self.directory / video_name).unlink()
                (self.directory / filename).unlink()

    @staticmethod
    def _merge_audio(
            video: pathlib.Path,
            audio: pathlib.Path,
            filename: pathlib.Path,
            directory: pathlib.Path):
        input_video = str(directory / video)
        input_audio = str(directory / audio)

        fnull = open(os.devnull, 'w')
        cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(
            input_audio, input_video, str(directory / filename))
        subprocess.call(cmd.split(), stdout=fnull, stderr=subprocess.STDOUT)

        (directory / video).unlink()
        (directory / audio).unlink()
