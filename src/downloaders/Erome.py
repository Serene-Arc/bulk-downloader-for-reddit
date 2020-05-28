import os
import urllib.request
from html.parser import HTMLParser

from src.downloaders.downloaderUtils import getFile
from src.downloaders.downloaderUtils import getExtension

from src.errors import (FileNameTooLong, AlbumNotDownloadedCompletely, 
                        NotADownloadableLinkError, FileAlreadyExistsError)
from src.utils import nameCorrector
from src.utils import printToFile as print

class Erome:
    def __init__(self,directory,post):
        try:
            IMAGES = self.getLinks(post['postURL'])
        except urllib.error.HTTPError:
            raise NotADownloadableLinkError("Not a downloadable link")

        imagesLenght = len(IMAGES)
        howManyDownloaded = imagesLenght
        duplicates = 0

        if imagesLenght == 1:
            
            extension = getExtension(IMAGES[0])

            """Filenames are declared here"""

            title = nameCorrector(post['postTitle'])
            print(post["postSubmitter"]+"_"+title+"_"+post['postId']+extension)

            fileDir = directory / (
                post["postSubmitter"]+"_"+title+"_"+post['postId']+extension
            )
            tempDir = directory / (
                post["postSubmitter"]+"_"+title+"_"+post['postId']+".tmp"
            )

            imageURL = IMAGES[0]
            if 'https://' not in imageURL and 'http://' not in imageURL:
                imageURL = "https://" + imageURL

            try:
                getFile(fileDir,tempDir,imageURL)
            except FileNameTooLong:
                fileDir = directory / (post['postId'] + extension)
                tempDir = directory / (post['postId'] + '.tmp')
                getFile(fileDir,tempDir,imageURL)

        else:
            title = nameCorrector(post['postTitle'])
            print(post["postSubmitter"]+"_"+title+"_"+post['postId'],end="\n\n")

            folderDir = directory / (
                post["postSubmitter"] + "_" + title + "_" + post['postId']
            )

            try:
                if not os.path.exists(folderDir):
                    os.makedirs(folderDir)
            except FileNotFoundError:
                folderDir = directory / post['postId']
                os.makedirs(folderDir)

            for i in range(imagesLenght):
                
                extension = getExtension(IMAGES[i])

                fileName = str(i+1)
                imageURL = IMAGES[i]
                if 'https://' not in imageURL and 'http://' not in imageURL:
                    imageURL = "https://" + imageURL

                fileDir = folderDir / (fileName + extension)
                tempDir = folderDir / (fileName + ".tmp")

                print("  ({}/{})".format(i+1,imagesLenght))
                print("  {}".format(fileName+extension))

                try:
                    getFile(fileDir,tempDir,imageURL,indent=2)
                    print()
                except FileAlreadyExistsError:
                    print("  The file already exists" + " "*10,end="\n\n")
                    duplicates += 1
                    howManyDownloaded -= 1

                except Exception as exception:
                    # raise exception
                    print("\n  Could not get the file")
                    print(
                        "  "
                        + "{class_name}: {info}".format(
                            class_name=exception.__class__.__name__,
                            info=str(exception)
                        )
                        + "\n"
                    )
                    howManyDownloaded -= 1

            if duplicates == imagesLenght:
                raise FileAlreadyExistsError
            elif howManyDownloaded + duplicates < imagesLenght:
                raise AlbumNotDownloadedCompletely(
                    "Album Not Downloaded Completely"
                )

    def getLinks(self,url,lineNumber=129):
 
        content = []
        lineNumber = None

        class EromeParser(HTMLParser):
            tag = None
            def handle_starttag(self, tag, attrs):
                self.tag = {tag:{attr[0]: attr[1] for attr in attrs}}

        pageSource = (urllib.request.urlopen(url).read().decode().split('\n'))

        """ FIND WHERE ALBUM STARTS IN ORDER NOT TO GET WRONG LINKS"""
        for i in range(len(pageSource)):
            obj = EromeParser()
            obj.feed(pageSource[i])
            tag = obj.tag
            
            if tag is not None:
                if "div" in tag:
                    if "id" in tag["div"]:
                        if tag["div"]["id"] == "album":
                            lineNumber = i
                            break

        for line in pageSource[lineNumber:]:
            obj = EromeParser()
            obj.feed(line)
            tag = obj.tag
            if tag is not None:
                if "img" in tag:
                    if "class" in tag["img"]:
                        if tag["img"]["class"]=="img-front":
                            content.append(tag["img"]["src"])
                elif "source" in tag:
                    content.append(tag["source"]["src"])
                    
        return [
            link for link in content \
            if link.endswith("_480p.mp4") or not link.endswith(".mp4")
        ]