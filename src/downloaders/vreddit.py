import os
import subprocess

from src.downloaders.downloaderUtils import getFile
from src.utils import GLOBAL
from src.utils import printToFile as print


class VReddit:
    def __init__(self, directory, post):
        extension = ".mp4"
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post) + extension
        shortFilename = post['POSTID'] + extension

        try:
            FNULL = open(os.devnull, 'w')
            subprocess.call("ffmpeg", stdout=FNULL, stderr=subprocess.STDOUT)
        except BaseException:
            getFile(filename, shortFilename, directory, post['CONTENTURL'])
            print("FFMPEG library not found, skipping merging video and audio")
        else:
            videoName = post['POSTID'] + "_video"
            videoURL = post['CONTENTURL']
            audioName = post['POSTID'] + "_audio"
            audioURL = videoURL[:videoURL.rfind('/')] + '/DASH_audio.mp4'

            print(directory, filename, sep="\n")

            getFile(videoName, videoName, directory, videoURL, silent=True)
            getFile(audioName, audioName, directory, audioURL, silent=True)
            try:
                self._mergeAudio(videoName,
                                 audioName,
                                 filename,
                                 shortFilename,
                                 directory)
            except KeyboardInterrupt:
                os.remove(directory / filename)
                os.remove(directory / audioName)

                os.rename(directory / videoName, directory / filename)

    @staticmethod
    def _mergeAudio(video, audio, filename, shortFilename, directory):

        inputVideo = str(directory / video)
        inputAudio = str(directory / audio)

        FNULL = open(os.devnull, 'w')
        cmd = f"ffmpeg -i {inputAudio} -i {inputVideo} -c:v copy -c:a aac -strict experimental {str(directory / filename)}"
        subprocess.call(cmd.split(), stdout=FNULL, stderr=subprocess.STDOUT)

        os.remove(directory / video)
        os.remove(directory / audio)
