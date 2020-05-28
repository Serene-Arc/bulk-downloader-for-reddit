import io
import os
from pathlib import Path

from src.errors import FileAlreadyExistsError
from src.utils import nameCorrector

VanillaPrint = print
from src.utils import printToFile as print

class SelfPost:
    def __init__(self,directory,post):
        if not os.path.exists(directory): os.makedirs(directory)

        title = nameCorrector(post['postTitle'])

        """Filenames are declared here"""

        print(post["postSubmitter"]+"_"+title+"_"+post['postId']+".md")

        fileDir = directory / (
            post["postSubmitter"]+"_"+title+"_"+post['postId']+".md"
        )
        
        if Path.is_file(fileDir):
            raise FileAlreadyExistsError
            
        try:
            self.writeToFile(fileDir,post)
        except FileNotFoundError:
            fileDir = post['postId']+".md"
            fileDir = directory / fileDir

            self.writeToFile(fileDir,post)
    
    @staticmethod
    def writeToFile(directory,post):
        
        """Self posts are formatted here"""
        content = ("## ["
                   + post["postTitle"]
                   + "]("
                   + post["postURL"]
                   + ")\n"
                   + post["postContent"]
                   + "\n\n---\n\n"
                   + "submitted to [r/"
                   + post["postSubreddit"]
                   + "](https://www.reddit.com/r/"
                   + post["postSubreddit"]
                   + ") by [u/"
                   + post["postSubmitter"]
                   + "](https://www.reddit.com/user/"
                   + post["postSubmitter"]
                   + ")")

        with io.open(directory,"w",encoding="utf-8") as FILE:
            VanillaPrint(content,file=FILE)
        
        print("Downloaded")
