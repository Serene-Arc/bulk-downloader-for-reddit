import io
import os
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import imgurpython
from multiprocessing import Queue

from src.errors import (AlbumNotDownloadedCompletely, FileAlreadyExistsError,
                        FileNameTooLong, ImgurLoginError,
                        NotADownloadableLinkError)
from src.tools import GLOBAL, nameCorrector, printToFile

VanillaPrint = print
print = printToFile

def dlProgress(count, blockSize, totalSize):
    """Function for writing download progress to console
    """

    downloadedMbs = int(count*blockSize*(10**(-6)))
    fileSize = int(totalSize*(10**(-6)))
    sys.stdout.write("\r{}Mb/{}Mb".format(downloadedMbs,fileSize))
    sys.stdout.write("\b"*len("\r{}Mb/{}Mb".format(downloadedMbs,fileSize)))
    sys.stdout.flush()

def getExtension(link):
    """Extract file extension from image link.
    If didn't find any, return '.jpg'
    """

    imageTypes = ['jpg','png','mp4','webm','gif']
    parsed = link.split('.')
    for TYPE in imageTypes:
        if TYPE in parsed:
            return "."+parsed[-1]
    else:
        if not "v.redd.it" in link:
            return '.jpg'
        else:
            return '.mp4'

def getFile(fileDir,tempDir,imageURL,indent=0):
    """Downloads given file to given directory.

    fileDir -- Full file directory
    tempDir -- Full file directory with the extension of '.tmp'
    imageURL -- URL to the file to be downloaded

    redditID -- Post's reddit id if renaming the file is necessary.
                As too long file names seem not working.
    """

    if not (os.path.isfile(fileDir)):
        for i in range(3):
            try:
                urllib.request.urlretrieve(imageURL,
                                           tempDir,
                                           reporthook=dlProgress)
                os.rename(tempDir,fileDir)
                print(" "*indent+"Downloaded"+" "*10)
                break
            except ConnectionResetError as exception:
                print(" "*indent + str(exception))
                print(" "*indent + "Trying again\n")
            except FileNotFoundError:
                raise FileNameTooLong
    else:
        raise FileAlreadyExistsError

class Erome:
    def __init__(self,directory,post):
        # try:
        #     IMAGES = self.getLinks(post['postURL'])
        # except IndexError:
        #     # raise NotADownloadableLinkError("Could not read the page source")
        #     pass
        # except Exception as exception:
        #     pass
        #     # raise NotADownloadableLinkError("Could not read the page source")
        IMAGES = self.getLinks(post['postURL'])

        imagesLenght = len(IMAGES)
        howManyDownloaded = imagesLenght
        duplicates = 0

        if imagesLenght == 1:
            
            extension = getExtension(IMAGES[0])

            title = nameCorrector(post['postTitle'])
            print(title+"_" +post['postId']+extension)

            fileDir = title + "_" + post['postId'] + extension
            fileDir = directory / fileDir

            tempDir = title + "_" + post['postId'] + '.tmp'
            tempDir = directory / tempDir

            imageURL = "https:" + IMAGES[0]

            try:
                getFile(fileDir,tempDir,imageURL)
            except FileNameTooLong:
                fileDir = directory / (post['postId'] + extension)
                tempDir = directory / (post['postId'] + '.tmp')
                getFile(fileDir,tempDir,imageURL)

        else:
            title = nameCorrector(post['postTitle'])
            print(title+"_"+post['postId'],end="\n\n")

            folderDir = directory / (title+"_"+post['postId'])

            try:
                if not os.path.exists(folderDir):
                    os.makedirs(folderDir)
            except FileNotFoundError:
                folderDir = directory / post['postId']
                os.makedirs(folderDir)

            for i in range(imagesLenght):
                
                extension = getExtension(IMAGES[i])

                fileName = str(i+1)
                imageURL = "https:" + IMAGES[i]

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
                    raise exception
                    print("\n  Could not get the file")
                    print("  " + str(exception) + "\n")
                    exceptionType = exception
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

class Imgur:
    def __init__(self,directory,post):
        self.imgurClient = self.initImgur()

        imgurID = self.getId(post['postURL'])
        content = self.getLink(imgurID)

        if not os.path.exists(directory): os.makedirs(directory)

        if content['type'] == 'image':

            try:
                post['mediaURL'] = content['object'].mp4
            except AttributeError:
                post['mediaURL'] = content['object'].link

            post['postExt'] = getExtension(post['mediaURL'])

            title = nameCorrector(post['postTitle'])
            print(title+"_" +post['postId']+post['postExt'])

            fileDir = title + "_" + post['postId'] + post['postExt']
            fileDir = directory / fileDir

            tempDir = title + "_" + post['postId'] + '.tmp'
            tempDir = directory / tempDir
            try:
                getFile(fileDir,tempDir,post['mediaURL'])
            except FileNameTooLong:
                fileDir = directory / post['postId'] + post['postExt']
                tempDir = directory / post['postId'] + '.tmp'
                getFile(fileDir,tempDir,post['mediaURL'])

        elif content['type'] == 'album':
            exceptionType = ""
            images = content['object'].images
            imagesLenght = len(images)
            howManyDownloaded = imagesLenght
            duplicates = 0

            title = nameCorrector(post['postTitle'])
            print(title+"_"+post['postId'],end="\n\n")

            folderDir = directory / (title+"_"+post['postId'])

            try:
                if not os.path.exists(folderDir):
                    os.makedirs(folderDir)
            except FileNotFoundError:
                folderDir = directory / post['postId']
                os.makedirs(folderDir)

            for i in range(imagesLenght):
                try:
                    imageURL = images[i]['mp4']
                except KeyError:
                    imageURL = images[i]['link']

                images[i]['Ext'] = getExtension(imageURL)

                fileName = (str(i+1)
                            + "_"
                            + nameCorrector(str(images[i]['title']))
                            + "_"
                            + images[i]['id'])

                fileDir = folderDir / (fileName + images[i]['Ext'])
                tempDir = folderDir / (fileName + ".tmp")

                print("  ({}/{})".format(i+1,imagesLenght))
                print("  {}".format(fileName+images[i]['Ext']))

                try:
                    getFile(fileDir,tempDir,imageURL,indent=2)
                    print()
                except FileAlreadyExistsError:
                    print("  The file already exists" + " "*10,end="\n\n")
                    duplicates += 1
                    howManyDownloaded -= 1

                # IF FILE NAME IS TOO LONG, IT WONT REGISTER
                except FileNameTooLong:
                    fileName = (str(i+1) + "_" + images[i]['id'])
                    fileDir = folderDir / (fileName + images[i]['Ext'])
                    tempDir = folderDir / (fileName + ".tmp")
                    try:
                        getFile(fileDir,tempDir,imageURL,indent=2)
                    # IF STILL TOO LONG
                    except FileNameTooLong:
                        fileName = str(i+1)
                        fileDir = folderDir / (fileName + images[i]['Ext'])
                        tempDir = folderDir / (fileName + ".tmp")
                        getFile(fileDir,tempDir,imageURL,indent=2)

                except Exception as exception:
                    print("\n  Could not get the file")
                    print("  " + str(exception) + "\n")
                    exceptionType = exception
                    howManyDownloaded -= 1

            if duplicates == imagesLenght:
                raise FileAlreadyExistsError
            elif howManyDownloaded + duplicates < imagesLenght:
                raise AlbumNotDownloadedCompletely(
                    "Album Not Downloaded Completely"
                )
    
    @staticmethod
    def initImgur():
        """Initialize imgur api"""

        config = GLOBAL.config
        return imgurpython.ImgurClient(
            config['imgur_client_id'],
            config['imgur_client_secret']
        )
    def getId(self,submissionURL):
        """Extract imgur post id
        and determine if its a single image or album
        """

        domainLenght = len("imgur.com/")
        if submissionURL[-1] == "/":
            submissionURL = submissionURL[:-1]

        if "a/" in submissionURL or "gallery/" in submissionURL:
            albumId = submissionURL.split("/")[-1]
            return {'id':albumId, 'type':'album'}

        else:
            url = submissionURL.replace('.','/').split('/')
            imageId = url[url.index('com')+1]
            return {'id':imageId, 'type':'image'}

    def getLink(self,identity):
        """Request imgur object from imgur api
        """

        if identity['type'] == 'image':
            return {'object':self.imgurClient.get_image(identity['id']),
                    'type':'image'}
        elif identity['type'] == 'album':
            return {'object':self.imgurClient.get_album(identity['id']),
                    'type':'album'}
    @staticmethod
    def get_credits():
        return Imgur.initImgur().get_credits()

class Gfycat:
    def __init__(self,directory,POST):
        try:
            POST['mediaURL'] = self.getLink(POST['postURL'])
        except IndexError:
            raise NotADownloadableLinkError("Could not read the page source")
        except Exception as exception:
            raise NotADownloadableLinkError("Could not read the page source")

        POST['postExt'] = getExtension(POST['mediaURL'])

        if not os.path.exists(directory): os.makedirs(directory)
        title = nameCorrector(POST['postTitle'])
        print(title+"_"+POST['postId']+POST['postExt'])

        fileDir = directory / (title+"_"+POST['postId']+POST['postExt'])
        tempDir = directory / (title+"_"+POST['postId']+".tmp")
        try:
            getFile(fileDir,tempDir,POST['mediaURL'])
        except FileNameTooLong:
            fileDir = directory / (POST['postId']+POST['postExt'])
            tempDir = directory / (POST['postId']+".tmp")

            getFile(fileDir,tempDir,POST['mediaURL'])
      
    def getLink(self, url, query='<source id="mp4Source" src=', lineNumber=105):
        """Extract direct link to the video from page's source
        and return it
        """

        if '.webm' in url or '.mp4' in url or '.gif' in url:
            return url

        if url[-1:] == '/':
            url = url[:-1]

        url = "https://gfycat.com/" + url.split('/')[-1]

        pageSource = (urllib.request.urlopen(url).read().decode().split('\n'))

        theLine = pageSource[lineNumber]
        lenght = len(query)
        link = []

        for i in range(len(theLine)):
            if theLine[i:i+lenght] == query:
                cursor = (i+lenght)+1
                while not theLine[cursor] == '"':
                    link.append(theLine[cursor])
                    cursor += 1
                break

        if "".join(link) == "":
            raise NotADownloadableLinkError("Could not read the page source")

        return "".join(link)

class Direct:
    def __init__(self,directory,POST):
        POST['postExt'] = getExtension(POST['postURL'])
        if not os.path.exists(directory): os.makedirs(directory)
        title = nameCorrector(POST['postTitle'])
        print(title+"_"+POST['postId']+POST['postExt'])

        fileDir = title+"_"+POST['postId']+POST['postExt']
        fileDir = directory / fileDir

        tempDir = title+"_"+POST['postId']+".tmp"
        tempDir = directory / tempDir

        try:
            getFile(fileDir,tempDir,POST['postURL'])
        except FileNameTooLong:
            fileDir = directory / (POST['postId']+POST['postExt'])
            tempDir = directory / (POST['postId']+".tmp")

            getFile(fileDir,tempDir,POST['postURL'])

class Self:
    def __init__(self,directory,post):
        if not os.path.exists(directory): os.makedirs(directory)

        title = nameCorrector(post['postTitle'])
        print(title+"_"+post['postId']+".md")

        fileDir = title+"_"+post['postId']+".md"
        fileDir = directory / fileDir
        
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

        content = ("## ["
                   + post["postTitle"]
                   + "]("
                   + post["postURL"]
                   + ")\n"
                   + post["postContent"]
                   + "\n\n---\n\n"
                   + "submitted by [u/"
                   + post["postSubmitter"]
                   + "](https://www.reddit.com/user/"
                   + post["postSubmitter"]
                   + ")")

        with io.open(directory,"w",encoding="utf-8") as FILE:
            VanillaPrint(content,file=FILE)
        
        print("Downloaded")
