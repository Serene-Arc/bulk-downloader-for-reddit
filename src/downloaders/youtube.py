import os
import youtube_dl
import sys

from src.downloaders.downloaderUtils import createHash

from src.utils import GLOBAL
from src.utils import printToFile as print
from src.errors import FileAlreadyExistsError


class Youtube:
    def __init__(self, directory, post):
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post)
        print(filename)

        self.download(filename, directory, post['CONTENTURL'])

    def download(self, filename, directory, url):
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
                fileHash = createHash(location)
            except FileNotFoundError:
                return None
            if fileHash in GLOBAL.downloadedPosts():
                os.remove(location)
                raise FileAlreadyExistsError
            GLOBAL.downloadedPosts.add(fileHash)

    @staticmethod
    def _hook(d):
        if d['status'] == 'finished':
            return print("Downloaded")
        downloadedMbs = int(d['downloaded_bytes'] * (10**(-6)))
        fileSize = int(d['total_bytes'] * (10**(-6)))
        sys.stdout.write("{}Mb/{}Mb\r".format(downloadedMbs, fileSize))
        sys.stdout.flush()
