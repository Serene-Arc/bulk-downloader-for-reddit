#!/usr/bin/env python

"""
This program downloads imgur, gfycat and direct image and video links of 
saved posts from a reddit account. It is written in Python 3.
"""

import argparse
import logging
import os
import sys
import time
from io import StringIO
from pathlib import Path, PurePath

from src.downloader import Direct, Gfycat, Imgur, Self, Erome
from src.errors import *
from src.parser import LinkDesigner
from src.searcher import getPosts
from src.tools import (GLOBAL, createLogFile, jsonFile, nameCorrector,
                       printToFile)

__author__ = "Ali Parlakci"
__license__ = "GPL"
__version__ = "1.3.1"
__maintainer__ = "Ali Parlakci"
__email__ = "parlakciali@gmail.com"

def getConfig(configFileName):
    """Read credentials from config.json file"""

    keys = ['imgur_client_id',
            'imgur_client_secret']

    if os.path.exists(configFileName):
        FILE = jsonFile(configFileName)
        content = FILE.read()
        if "reddit_refresh_token" in content:
            if content["reddit_refresh_token"] == "":
                FILE.delete("reddit_refresh_token")
        for key in keys:
            try:
                if content[key] == "":
                    raise KeyError
            except KeyError:
                print(key,": ")
                FILE.add({key:input()})
        return jsonFile(configFileName).read()

    else:
        FILE = jsonFile(configFileName)
        configDictionary = {}
        for key in keys:
            configDictionary[key] = input(key + ": ")
        FILE.add(configDictionary)
        return FILE.read()

def parseArguments(arguments=[]):
    """Initialize argparse and add arguments"""

    parser = argparse.ArgumentParser(allow_abbrev=False,
                                     description="This program downloads " \
                                                 "media from reddit " \
                                                 "posts")
    parser.add_argument("--directory",
                        help="Specifies the directory where posts will be " \
                        "downloaded to",
                        metavar="DIRECTORY")

    parser.add_argument("--link","-l",
                        help="Get posts from link",
                        metavar="link")

    parser.add_argument("--saved",
                        action="store_true",
                        help="Triggers saved mode")

    parser.add_argument("--submitted",
                        action="store_true",
                        help="Gets posts of --user")

    parser.add_argument("--upvoted",
                        action="store_true",
                        help="Gets upvoted posts of --user")

    parser.add_argument("--log",
                        help="Takes a log file which created by itself " \
                             "(json files), reads posts and tries downloadin" \
                             "g them again.",
                        # type=argparse.FileType('r'),
                        metavar="LOG FILE")

    parser.add_argument("--subreddit",
                        nargs="+",
                        help="Triggers subreddit mode and takes subreddit's " \
                             "name without r/. use \"frontpage\" for frontpage",
                        metavar="SUBREDDIT",
                        type=str)
    
    parser.add_argument("--multireddit",
                        help="Triggers multireddit mode and takes "\
                             "multireddit's name without m/",
                        metavar="MULTIREDDIT",
                        type=str)

    parser.add_argument("--user",
                        help="reddit username if needed. use \"me\" for " \
                             "current user",
                        required="--multireddit" in sys.argv or \
                                 "--submitted" in sys.argv,
                        metavar="redditor",
                        type=str)

    parser.add_argument("--search",
                        help="Searches for given query in given subreddits",
                        metavar="query",
                        type=str)

    parser.add_argument("--sort",
                        help="Either hot, top, new, controversial, rising " \
                             "or relevance default: hot",
                        choices=[
                            "hot","top","new","controversial","rising",
                            "relevance"
                        ],
                        metavar="SORT TYPE",
                        type=str)

    parser.add_argument("--limit",
                        help="default: unlimited",
                        metavar="Limit",
                        type=int)

    parser.add_argument("--time",
                        help="Either hour, day, week, month, year or all." \
                             " default: all",
                        choices=["all","hour","day","week","month","year"],
                        metavar="TIME_LIMIT",
                        type=str)
    
    parser.add_argument("--NoDownload",
                        help="Just gets the posts and store them in a file" \
                             " for downloading later",
                        action="store_true",
                        default=False)
    

    if arguments == []:
        return parser.parse_args()
    else:
        return parser.parse_args(arguments)

def checkConflicts():
    """Check if command-line arguments are given correcly,
    if not, raise errors
    """

    if GLOBAL.arguments.user is None:
        user = 0
    else:
        user = 1

    modes = [
        "saved","subreddit","submitted","search","log","link","upvoted",
        "multireddit"
    ]

    values = {
        x: 0 if getattr(GLOBAL.arguments,x) is None or \
                getattr(GLOBAL.arguments,x) is False \
             else 1 \
             for x in modes
    }

    if not sum(values[x] for x in values) == 1:
        raise ProgramModeError("Invalid program mode")
    
    if values["search"]+values["saved"] == 2:
        raise SearchModeError("You cannot search in your saved posts")

    if values["search"]+values["submitted"] == 2:
        raise SearchModeError("You cannot search in submitted posts")

    if values["search"]+values["upvoted"] == 2:
        raise SearchModeError("You cannot search in upvoted posts")

    if values["upvoted"]+values["submitted"] == 1 and user == 0:
        raise RedditorNameError("No redditor name given")

class PromptUser:
    @staticmethod
    def chooseFrom(choices):
        print()
        choicesByIndex = list(str(x) for x in range(len(choices)+1))
        for i in range(len(choices)):
            print("{indent}[{order}] {mode}".format(
                indent=" "*4,order=i+1,mode=choices[i]
            ))
        print(" "*4+"[0] exit\n")
        choice = input("> ")
        while not choice.lower() in choices+choicesByIndex+["exit"]:
            print("Invalid input\n")
            programModeIndex = input("> ")

        if choice == "0" or choice == "exit":
            sys.exit()
        elif choice in choicesByIndex:
            return choices[int(choice)-1]
        else:
            return choice
    
    def __init__(self):
        print("select program mode:")
        programModes = [
            "search","subreddit","multireddit",
            "submitted","upvoted","saved","log"
        ]
        programMode = self.chooseFrom(programModes)

        if programMode == "search":
            GLOBAL.arguments.search = input("\nquery: ")
            GLOBAL.arguments.subreddit = input("\nsubreddit: ")

            print("\nselect sort type:")
            sortTypes = [
                "relevance","top","new"
            ]
            sortType = self.chooseFrom(sortTypes)
            GLOBAL.arguments.sort = sortType

            print("\nselect time filter:")
            timeFilters = [
                "hour","day","week","month","year","all"
            ]
            timeFilter = self.chooseFrom(timeFilters)
            GLOBAL.arguments.time = timeFilter

        if programMode == "subreddit":

            subredditInput = input("subreddit (enter frontpage for frontpage): ")
            GLOBAL.arguments.subreddit = subredditInput

            while not (subredditInput == "" or subredditInput.lower() == "frontpage"):
                subredditInput = input("subreddit: ")
                GLOBAL.arguments.subreddit += "+" + subredditInput

            if " " in GLOBAL.arguments.subreddit:
                GLOBAL.arguments.subreddit = "+".join(GLOBAL.arguments.subreddit.split())

            # DELETE THE PLUS (+) AT THE END
            if not subredditInput.lower() == "frontpage":
                GLOBAL.arguments.subreddit = GLOBAL.arguments.subreddit[:-1]

            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","rising","controversial"
            ]
            sortType = self.chooseFrom(sortTypes)
            GLOBAL.arguments.sort = sortType

            if sortType in ["top","controversial"]:
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self.chooseFrom(timeFilters)
                GLOBAL.arguments.time = timeFilter
            else:
                GLOBAL.arguments.time = "all"

        elif programMode == "multireddit":
            GLOBAL.arguments.user = input("\nredditor: ")
            GLOBAL.arguments.multireddit = input("\nmultireddit: ")
            
            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","rising","controversial"
            ]
            sortType = self.chooseFrom(sortTypes)
            GLOBAL.arguments.sort = sortType

            if sortType in ["top","controversial"]:
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self.chooseFrom(timeFilters)
                GLOBAL.arguments.time = timeFilter
            else:
                GLOBAL.arguments.time = "all"
        
        elif programMode == "submitted":
            GLOBAL.arguments.submitted = True
            GLOBAL.arguments.user = input("\nredditor: ")

            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","controversial"
            ]
            sortType = self.chooseFrom(sortTypes)
            GLOBAL.arguments.sort = sortType

            if sortType == "top":
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self.chooseFrom(timeFilters)
                GLOBAL.arguments.time = timeFilter
            else:
                GLOBAL.arguments.time = "all"
        
        elif programMode == "upvoted":
            GLOBAL.arguments.upvoted = True
            GLOBAL.arguments.user = input("\nredditor: ")
        
        elif programMode == "saved":
            GLOBAL.arguments.saved = True
        
        elif programMode == "log":
            while True:
                GLOBAL.arguments.log = input("\nlog file directory:")
                if Path(GLOBAL.arguments.log ).is_file():
                    break 
        while True:
            try:
                GLOBAL.arguments.limit = int(input("\nlimit (0 for none): "))
                if GLOBAL.arguments.limit == 0:
                    GLOBAL.arguments.limit = None
                break
            except ValueError:
                pass

def prepareAttributes():
    ATTRIBUTES = {}

    if GLOBAL.arguments.user is not None:
        ATTRIBUTES["user"] = GLOBAL.arguments.user

    if GLOBAL.arguments.search is not None:
        ATTRIBUTES["search"] = GLOBAL.arguments.search
        if GLOBAL.arguments.sort == "hot" or \
           GLOBAL.arguments.sort == "controversial" or \
           GLOBAL.arguments.sort == "rising":
            GLOBAL.arguments.sort = "relevance"

    if GLOBAL.arguments.sort is not None:
        ATTRIBUTES["sort"] = GLOBAL.arguments.sort
    else:
        if GLOBAL.arguments.submitted:
            ATTRIBUTES["sort"] = "new"
        else:
            ATTRIBUTES["sort"] = "hot"

    if GLOBAL.arguments.time is not None:
        ATTRIBUTES["time"] = GLOBAL.arguments.time
    else:
        ATTRIBUTES["time"] = "all"

    if GLOBAL.arguments.link is not None:

        GLOBAL.arguments.link = GLOBAL.arguments.link.strip("\"")

        try:
            ATTRIBUTES = LinkDesigner(GLOBAL.arguments.link)
        except InvalidRedditLink:
            raise InvalidRedditLink

        if GLOBAL.arguments.search is not None:
            ATTRIBUTES["search"] = GLOBAL.arguments.search

        if GLOBAL.arguments.sort is not None:
            ATTRIBUTES["sort"] = GLOBAL.arguments.sort

        if GLOBAL.arguments.time is not None:
            ATTRIBUTES["time"] = GLOBAL.arguments.time

    elif GLOBAL.arguments.subreddit is not None:
        if type(GLOBAL.arguments.subreddit) == list:    
            GLOBAL.arguments.subreddit = "+".join(GLOBAL.arguments.subreddit)

        ATTRIBUTES["subreddit"] = GLOBAL.arguments.subreddit

    elif GLOBAL.arguments.multireddit is not None:
        ATTRIBUTES["multireddit"] = GLOBAL.arguments.multireddit

    elif GLOBAL.arguments.saved is True:
        ATTRIBUTES["saved"] = True

    elif GLOBAL.arguments.upvoted is True:
        ATTRIBUTES["upvoted"] = True

    elif GLOBAL.arguments.submitted is not None:
        ATTRIBUTES["submitted"] = True

        if GLOBAL.arguments.sort == "rising":
            raise InvalidSortingType
    
    ATTRIBUTES["limit"] = GLOBAL.arguments.limit

    return ATTRIBUTES

def postFromLog(fileName):
    """Analyze a log file and return a list of dictionaries containing
    submissions
    """
    if Path.is_file(Path(fileName)):
        content = jsonFile(fileName).read()
    else:
        print("File not found")
        sys.exit()

    try:
        del content["HEADER"]
    except KeyError:
        pass

    posts = []

    for post in content:
        if not content[post][-1]['postType'] == None:
            posts.append(content[post][-1])

    return posts

def postExists(POST):
    """Figure out a file's name and checks if the file already exists"""

    title = nameCorrector(POST['postTitle'])
    FILENAME = title + "_" + POST['postId']
    PATH = GLOBAL.directory / POST["postSubreddit"]
    possibleExtensions = [".jpg",".png",".mp4",".gif",".webm",".md"]

    for i in range(2):
        for extension in possibleExtensions:
            FILE_PATH = PATH / (FILENAME+extension)
            if FILE_PATH.exists():
                return True
        else:
            FILENAME = POST['postId']
    else:
        return False

def downloadPost(SUBMISSION):
    directory = GLOBAL.directory / SUBMISSION['postSubreddit']

    global lastRequestTime

    downloaders = {
        "imgur":Imgur,"gfycat":Gfycat,"erome":Erome,"direct":Direct,"self":Self
    }

    if SUBMISSION['postType'] in downloaders:

        print(SUBMISSION['postType'].upper())

        if SUBMISSION['postType'] == "imgur":
            
            if int(time.time() - lastRequestTime) <= 2:
                pass

            credit = Imgur.get_credits()

            IMGUR_RESET_TIME = credit['UserReset']-time.time()
            USER_RESET = ("after " \
                            + str(int(IMGUR_RESET_TIME/60)) \
                            + " Minutes " \
                            + str(int(IMGUR_RESET_TIME%60)) \
                            + " Seconds") 

            print(
                "Client: {} - User: {} - Reset {}".format(
                    credit['ClientRemaining'],
                    credit['UserRemaining'],
                    USER_RESET
                )
            )

            if not (credit['UserRemaining'] == 0 or \
                    credit['ClientRemaining'] == 0):

                """This block of code is needed
                """
                if int(time.time() - lastRequestTime) <= 2:
                    pass

                lastRequestTime = time.time()

            else:
                if credit['UserRemaining'] == 0:
                    KEYWORD = "user"
                elif credit['ClientRemaining'] == 0:
                    KEYWORD = "client"

                raise ImgurLimitError('{} LIMIT EXCEEDED\n'.format(KEYWORD.upper()))

        downloaders[SUBMISSION['postType']] (directory,SUBMISSION)

    else:
        raise NoSuitablePost

    return None

def download(submissions):
    """Analyze list of submissions and call the right function
    to download each one, catch errors, update the log files
    """

    subsLenght = len(submissions)
    global lastRequestTime
    lastRequestTime = 0
    downloadedCount = subsLenght
    duplicates = 0

    FAILED_FILE = createLogFile("FAILED")

    for i in range(subsLenght):
        print("\n({}/{})".format(i+1,subsLenght))
        print(
            "https://reddit.com/r/{subreddit}/comments/{id}".format(
                subreddit=submissions[i]['postSubreddit'],
                id=submissions[i]['postId']
            )
        )

        if postExists(submissions[i]):
            print(submissions[i]['postType'].upper())
            print("It already exists")
            duplicates += 1
            downloadedCount -= 1
            continue

        try:
            downloadPost(submissions[i])
        
        except FileAlreadyExistsError:
            print("It already exists")
            duplicates += 1
            downloadedCount -= 1

        except ImgurLoginError:
            print(
                "Imgur login failed. \nQuitting the program "\
                "as unexpected errors might occur."
            )
            sys.exit()

        except ImgurLimitError as exception:
            FAILED_FILE.add({int(i+1):[str(exception),submissions[i]]})
            downloadedCount -= 1

        except NotADownloadableLinkError as exception:
            print(exception)
            FAILED_FILE.add({int(i+1):[str(exception),submissions[i]]})
            downloadedCount -= 1

        except NoSuitablePost:
            print("No match found, skipping...")
            downloadedCount -= 1
        
        except Exception as exception:
            # raise exception
            print(exception)
            FAILED_FILE.add({int(i+1):[str(exception),submissions[i]]})
            downloadedCount -= 1

    if duplicates:
        print("\n There was {} duplicates".format(duplicates))

    if downloadedCount == 0:
        print(" Nothing downloaded :(")

    else:
        print(" Total of {} links downloaded!".format(downloadedCount))

def main():
    GLOBAL.arguments = parseArguments()

    if GLOBAL.arguments.directory is not None:
        GLOBAL.directory = Path(GLOBAL.arguments.directory)
    else:
        GLOBAL.directory = Path(input("download directory: "))

    print("\n"," ".join(sys.argv),"\n")

    try:
        checkConflicts()
    except ProgramModeError as err:
        PromptUser()
    except Exception as err:
        print(err)
        sys.exit()

    if not Path(GLOBAL.configDirectory).is_dir():
        os.makedirs(GLOBAL.configDirectory)
    GLOBAL.config = getConfig(GLOBAL.configDirectory / "config.json")

    if GLOBAL.arguments.log is not None:
        logDir = Path(GLOBAL.arguments.log)
        download(postFromLog(logDir))
        sys.exit()
    
    try:
        POSTS = getPosts(prepareAttributes())
    except InsufficientPermission:
        print("You do not have permission to do that")
        sys.exit()
    except NoMatchingSubmissionFound:
        print("No matching submission was found")
        sys.exit()
    except NoRedditSupoort:
        print("Reddit does not support that")
        sys.exit()
    except NoPrawSupport:
        print("PRAW does not support that")
        sys.exit()
    except MultiredditNotFound:
        print("Multireddit not found")
        sys.exit()
    except InvalidSortingType:
        print("Invalid sorting type has given")
        sys.exit()
    except InvalidRedditLink:
        print("Invalid reddit link")
        sys.exit()

    if POSTS is None:
        print("I could not find any posts in that URL")
        sys.exit()

    if GLOBAL.arguments.NoDownload:
        sys.exit()

    else:
        download(POSTS)

if __name__ == "__main__":

    log_stream = StringIO()    
    logging.basicConfig(stream=log_stream, level=logging.INFO)

    try:
        VanillaPrint = print
        print = printToFile
        GLOBAL.RUN_TIME = time.time()
        main()

    except KeyboardInterrupt:
        if GLOBAL.directory is None:
            GLOBAL.directory = Path(".\\")
        print("\nQUITTING...")
        
    except Exception as exception:
        if GLOBAL.directory is None:
            GLOBAL.directory = Path(".\\")
        logging.error(sys.exc_info()[0].__name__,
                      exc_info=full_exc_info(sys.exc_info()))
        print(log_stream.getvalue())

    input("\nPress enter to quit\n")
