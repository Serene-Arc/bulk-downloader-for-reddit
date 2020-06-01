import io
import os
from pathlib import Path

from src.errors import FileAlreadyExistsError
from src.utils import GLOBAL

VanillaPrint = print
from src.utils import printToFile as print

class SelfPost:
    def __init__(self,directory,post):
        if not os.path.exists(directory): os.makedirs(directory)

        filename = GLOBAL.config['filename'].format(**post)

        fileDir = directory / (filename+".md")
        print(fileDir)
        print(filename+".md")


        if Path.is_file(fileDir):
            raise FileAlreadyExistsError
            
        try:
            self.writeToFile(fileDir,post)
        except FileNotFoundError:
            fileDir = post['POSTID']+".md"
            fileDir = directory / fileDir

            self.writeToFile(fileDir,post)
    
    @staticmethod
    def writeToFile(directory,post):
        
        """Self posts are formatted here"""
        content = ("## ["
                   + post["TITLE"]
                   + "]("
                   + post["CONTENTURL"]
                   + ")\n"
                   + post["CONTENT"]
                   + "\n\n---\n\n"
                   + "submitted to [r/"
                   + post["SUBREDDIT"]
                   + "](https://www.reddit.com/r/"
                   + post["SUBREDDIT"]
                   + ") by [u/"
                   + post["REDDITOR"]
                   + "](https://www.reddit.com/user/"
                   + post["REDDITOR"]
                   + ")")

        with io.open(directory,"w",encoding="utf-8") as FILE:
            VanillaPrint(content,file=FILE)
        
        print("Downloaded")
