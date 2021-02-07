import os
import pathlib
import sys

import youtube_dl

from bulkredditdownloader.downloaders.base_downloader import BaseDownloader
from bulkredditdownloader.errors import FileAlreadyExistsError
from bulkredditdownloader.utils import GLOBAL
from bulkredditdownloader.utils import printToFile as print


class Youtube(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: dict):
        super().__init__(directory, post)
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post)
        print(filename)

        self.download(filename, directory, post['CONTENTURL'])

    def download(self, filename: str, directory: pathlib.Path, url: str):
        ydl_opts = {
            "format": "best",
            "outtmpl": str(directory / (filename + ".%(ext)s")),
            "progress_hooks": [self._hook],
            "playlistend": 1,
            "nooverwrites": True,
            "quiet": True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        location = directory / (filename + ".mp4")

        if GLOBAL.arguments.no_dupes:
            try:
                file_hash = self.createHash(str(location))
            except FileNotFoundError:
                return None
            if file_hash in GLOBAL.downloadedPosts():
                os.remove(location)
                raise FileAlreadyExistsError
            GLOBAL.downloadedPosts.add(file_hash)

    @staticmethod
    def _hook(d):
        if d['status'] == 'finished':
            return print("Downloaded")
        downloaded_mbs = int(d['downloaded_bytes'] * (10**(-6)))
        file_size = int(d['total_bytes'] * (10**(-6)))
        sys.stdout.write("{}Mb/{}Mb\r".format(downloaded_mbs, file_size))
        sys.stdout.flush()
