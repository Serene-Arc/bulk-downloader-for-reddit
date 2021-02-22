#!/usr/bin/env python3

"""
This program downloads imgur, gfycat and direct image and video links of 
saved posts from a reddit account. It is written in Python 3.
"""

import argparse
import logging
import os
import sys
import time
import webbrowser
from io import StringIO
from pathlib import Path, PurePath
from prawcore.exceptions import InsufficientScope

from src.downloaders.Direct import Direct
from src.downloaders.Erome import Erome
from src.downloaders.Gfycat import Gfycat
from src.downloaders.Imgur import Imgur
from src.downloaders.redgifs import Redgifs
from src.downloaders.selfPost import SelfPost
from src.downloaders.vreddit import VReddit
from src.downloaders.youtube import Youtube
from src.downloaders.gifDeliveryNetwork import GifDeliveryNetwork
from src.downloaders.gallery import gallery
from src.errors import ImgurLimitError, NoSuitablePost, FileAlreadyExistsError, ImgurLoginError, NotADownloadableLinkError, NoSuitablePost, InvalidJSONFile, FailedToDownload, TypeInSkip, DomainInSkip, AlbumNotDownloadedCompletely, full_exc_info
from src.parser import LinkDesigner
from src.searcher import getPosts
from src.utils import (GLOBAL, createLogFile, nameCorrector,
                       printToFile)
from src.jsonHelper import JsonFile
from src.config import Config
from src.arguments import Arguments
from src.programMode import ProgramMode
from src.reddit import Reddit
from src.store import Store

__author__ = "Ali Parlakci"
__license__ = "GPL"
__version__ = "1.9.4"
__maintainer__ = "Ali Parlakci"
__email__ = "parlakciali@gmail.com"

def postFromLog(fileName):
    """Analyze a log file and return a list of dictionaries containing
    submissions
    """
    if Path.is_file(Path(fileName)):
        content = JsonFile(fileName).read()
    else:
        print("File not found")
        sys.exit()

    try:
        del content["HEADER"]
    except KeyError:
        pass

    posts = []

    for post in content:
        if not content[post][-1]['TYPE'] == None:
            posts.append(content[post][-1])

    return posts

def isPostExists(POST,directory):
    """Figure out a file's name and checks if the file already exists"""

    filename = GLOBAL.config['filename'].format(**POST)

    possibleExtensions = [".jpg",".png",".mp4",".gif",".webm",".md",".mkv",".flv"]

    for extension in possibleExtensions:

        path = directory / Path(filename+extension)

        if path.exists():
            return True

    else:
        return False

def downloadPost(SUBMISSION,directory):

    downloaders = {
        "imgur":Imgur,"gfycat":Gfycat,"erome":Erome,"direct":Direct,"self":SelfPost,
        "redgifs":Redgifs, "gifdeliverynetwork": GifDeliveryNetwork,
        "v.redd.it": VReddit, "youtube": Youtube, "gallery": gallery
    }

    print()
    if SUBMISSION['TYPE'] in downloaders:
        downloaders[SUBMISSION['TYPE']] (directory,SUBMISSION)
    else:
        raise NoSuitablePost

    return None

def download(submissions):
    """Analyze list of submissions and call the right function
    to download each one, catch errors, update the log files
    """

    downloadedCount = 0
    duplicates = 0

    FAILED_FILE = createLogFile("FAILED")

    if GLOBAL.arguments.unsave:
        reddit = Reddit(GLOBAL.config['credentials']['reddit']).begin()

    subsLenght = len(submissions)
        
    for i in range(len(submissions)):
        print(f"\n({i+1}/{subsLenght})",end=" — ")
        print(submissions[i]['POSTID'],
              f"r/{submissions[i]['SUBREDDIT']}",
              f"u/{submissions[i]['REDDITOR']}",
              submissions[i]['FLAIR'] if submissions[i]['FLAIR'] else "",
              sep=" — ",
              end="")
        print(f" – {submissions[i]['TYPE'].upper()}",end="",noPrint=True)

        directory = GLOBAL.directory / GLOBAL.config["folderpath"].format(**submissions[i])
        details = {
            **submissions[i], 
            **{
                "TITLE": nameCorrector(
                    submissions[i]['TITLE'],
                    reference = str(directory)
                                + GLOBAL.config['filename'].format(**submissions[i])
                                + ".ext"
                )
            }
        }
        filename = GLOBAL.config['filename'].format(**details)

        if isPostExists(details,directory):
            print()
            print(directory)
            print(filename)
            print("It already exists")
            duplicates += 1
            continue

        if any(domain in submissions[i]['CONTENTURL'] for domain in GLOBAL.arguments.skip):
            print()
            print(submissions[i]['CONTENTURL'])
            print("Domain found in skip domains, skipping post...")
            continue

        try:
            downloadPost(details,directory)
            GLOBAL.downloadedPosts.add(details['POSTID'])
            try:
                if GLOBAL.arguments.unsave:
                    reddit.submission(id=details['POSTID']).unsave()
            except InsufficientScope:
                reddit = Reddit().begin()
                reddit.submission(id=details['POSTID']).unsave()
              
            downloadedCount += 1
              
        except FileAlreadyExistsError:
            print("It already exists")
            GLOBAL.downloadedPosts.add(details['POSTID'])
            duplicates += 1

        except ImgurLoginError:
            print(
                "Imgur login failed. \nQuitting the program "\
                "as unexpected errors might occur."
            )
            sys.exit()

        except ImgurLimitError as exception:
            FAILED_FILE.add({int(i+1):[
                "{class_name}: {info}".format(
                    class_name=exception.__class__.__name__,info=str(exception)
                ),
                details
            ]})

        except NotADownloadableLinkError as exception:
            print(
                "{class_name}: {info}".format(
                    class_name=exception.__class__.__name__,info=str(exception)
                )
            )
            FAILED_FILE.add({int(i+1):[
                "{class_name}: {info}".format(
                    class_name=exception.__class__.__name__,info=str(exception)
                ),
                submissions[i]
            ]})

        except TypeInSkip:
            print()
            print(submissions[i]['CONTENTURL'])
            print("Skipping post...")

        except DomainInSkip:
            print()
            print(submissions[i]['CONTENTURL'])
            print("Skipping post...")

        except NoSuitablePost:
            print("No match found, skipping...")

        except FailedToDownload:
            print("Failed to download the posts, skipping...")
        except AlbumNotDownloadedCompletely:
            print("Album did not downloaded completely.")
            FAILED_FILE.add({int(i+1):[
                "{class_name}: {info}".format(
                    class_name=exc.__class__.__name__,info=str(exc)
                ),
                submissions[i]
            ]})
        
        except Exception as exc:
            print(
                "{class_name}: {info}\nSee CONSOLE_LOG.txt for more information".format(
                    class_name=exc.__class__.__name__,info=str(exc)
                )
            )

            logging.error(sys.exc_info()[0].__name__,
                          exc_info=full_exc_info(sys.exc_info()))
            print(GLOBAL.log_stream.getvalue(),noPrint=True)

            FAILED_FILE.add({int(i+1):[
                "{class_name}: {info}".format(
                    class_name=exc.__class__.__name__,info=str(exc)
                ),
                submissions[i]
            ]})

    if duplicates:
        print(f"\nThere {'were' if duplicates > 1 else 'was'} " \
              f"{duplicates} duplicate{'s' if duplicates > 1 else ''}")

    if downloadedCount == 0:
        print("Nothing is downloaded :(")

    else:
        print(f"Total of {downloadedCount} " \
              f"link{'s' if downloadedCount > 1 else ''} downloaded!")

def printLogo():
    VanillaPrint(
        f"\nBulk Downloader for Reddit v{__version__}\n" \
        f"Written by Ali PARLAKCI – parlakciali@gmail.com\n\n" \
        f"https://github.com/aliparlakci/bulk-downloader-for-reddit/\n"
    )

def main():
    
    if Path("config.json").exists():
        GLOBAL.configDirectory = Path("config.json")
    else:
        if not Path(GLOBAL.defaultConfigDirectory).is_dir():
            os.makedirs(GLOBAL.defaultConfigDirectory)
        GLOBAL.configDirectory = GLOBAL.defaultConfigDirectory  / "config.json"
    try:
        GLOBAL.config = Config(GLOBAL.configDirectory).generate()
    except InvalidJSONFile as exception:
        VanillaPrint(str(exception.__class__.__name__),">>",str(exception))
        VanillaPrint("Resolve it or remove it to proceed")
        input("\nPress enter to quit")
        sys.exit()

    sys.argv = sys.argv + GLOBAL.config["options"].split()

    arguments = Arguments.parse()
    GLOBAL.arguments = arguments

    if arguments.set_filename:
        Config(GLOBAL.configDirectory).setCustomFileName()
        sys.exit()

    if arguments.set_folderpath:
        Config(GLOBAL.configDirectory).setCustomFolderPath()
        sys.exit()

    if arguments.set_default_directory:
        Config(GLOBAL.configDirectory).setDefaultDirectory()
        sys.exit()

    if arguments.set_default_options:
        Config(GLOBAL.configDirectory).setDefaultOptions()
        sys.exit()

    if arguments.use_local_config:
        JsonFile("config.json").add(GLOBAL.config)
        sys.exit()
        
    if arguments.directory:
        GLOBAL.directory = Path(arguments.directory.strip())
    elif "default_directory" in GLOBAL.config and GLOBAL.config["default_directory"] != "":
        GLOBAL.directory = Path(GLOBAL.config["default_directory"].format(time=GLOBAL.RUN_TIME))
    else:
        GLOBAL.directory = Path(input("\ndownload directory: ").strip())

    if arguments.downloaded_posts:
        GLOBAL.downloadedPosts = Store(arguments.downloaded_posts)
    else:
        GLOBAL.downloadedPosts = Store()

    printLogo()
    print("\n"," ".join(sys.argv),"\n",noPrint=True)

    if arguments.log is not None:
        logDir = Path(arguments.log)
        download(postFromLog(logDir))
        sys.exit()


    programMode = ProgramMode(arguments).generate()

    try:
        posts = getPosts(programMode)
    except Exception as exc:
        logging.error(sys.exc_info()[0].__name__,
                      exc_info=full_exc_info(sys.exc_info()))
        print(GLOBAL.log_stream.getvalue(),noPrint=True)
        print(exc)
        sys.exit()

    if posts is None:
        print("I could not find any posts in that URL")
        sys.exit()

    if GLOBAL.arguments.no_download: pass
    else: download(posts)

if __name__ == "__main__":

    GLOBAL.log_stream = StringIO()    
    logging.basicConfig(stream=GLOBAL.log_stream, level=logging.INFO)

    try:
        VanillaPrint = print
        print = printToFile
        GLOBAL.RUN_TIME = str(time.strftime(
                                      "%d-%m-%Y_%H-%M-%S",
                                      time.localtime(time.time())
                                      ))
        main()

    except KeyboardInterrupt:
        if GLOBAL.directory is None:
            GLOBAL.directory = Path("..\\")
        
    except Exception as exception:
        if GLOBAL.directory is None:
            GLOBAL.directory = Path("..\\")
        logging.error(sys.exc_info()[0].__name__,
                      exc_info=full_exc_info(sys.exc_info()))
        print(GLOBAL.log_stream.getvalue())

    if not GLOBAL.arguments.quit: input("\nPress enter to quit\n")
              
