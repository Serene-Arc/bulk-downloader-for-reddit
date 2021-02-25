import os
import sys
import random
import socket
import time
import webbrowser
import urllib.request
from urllib.error import HTTPError

import praw
from prawcore.exceptions import NotFound, ResponseException, Forbidden

from src.reddit import Reddit
from src.utils import GLOBAL, createLogFile, printToFile
from src.jsonHelper import JsonFile
from src.errors import (NoMatchingSubmissionFound, NoPrawSupport,
                        NoRedditSupport, MultiredditNotFound,
                        InvalidSortingType, RedditLoginFailed,
                        InsufficientPermission, DirectLinkNotFound)

print = printToFile

def getPosts(programMode):
    """Call PRAW regarding to arguments and pass it to extractDetails.
    Return what extractDetails has returned.
    """

    reddit = Reddit(GLOBAL.config["credentials"]["reddit"]).begin()

    if programMode["sort"] == "best":
        raise NoPrawSupport("PRAW does not support that")

    if "subreddit" in programMode:
        if "search" in programMode:
            if programMode["subreddit"] == "frontpage":
                programMode["subreddit"] = "all"

    if "user" in programMode:
        if programMode["user"] == "me":
            programMode["user"] = str(reddit.user.me())

    if not "search" in programMode:
        if programMode["sort"] == "top" or programMode["sort"] == "controversial":
            keyword_params = {
                "time_filter":programMode["time"],
                "limit":programMode["limit"]
            }
        # OTHER SORT TYPES DON'T TAKE TIME_FILTER
        else:
            keyword_params = {
                "limit":programMode["limit"]
            }
    else:
        keyword_params = {
                "time_filter":programMode["time"],
                "limit":programMode["limit"]
            }

    if "search" in programMode:
        if programMode["sort"] in ["hot","rising","controversial"]:
            raise InvalidSortingType("Invalid sorting type has given")

        if "subreddit" in programMode:
            print (
                "search for \"{search}\" in\n" \
                "subreddit: {subreddit}\nsort: {sort}\n" \
                "time: {time}\nlimit: {limit}\n".format(
                    search=programMode["search"],
                    limit=programMode["limit"],
                    sort=programMode["sort"],
                    subreddit=programMode["subreddit"],
                    time=programMode["time"]
                ).upper(),noPrint=True
            )            
            return extractDetails(
                reddit.subreddit(programMode["subreddit"]).search(
                    programMode["search"],
                    limit=programMode["limit"],
                    sort=programMode["sort"],
                    time_filter=programMode["time"]
                )
            )

        elif "multireddit" in programMode:
            raise NoPrawSupport("PRAW does not support that")
        
        elif "user" in programMode:
            raise NoPrawSupport("PRAW does not support that")

        elif "saved" in programMode:
            raise ("Reddit does not support that")
    
    if programMode["sort"] == "relevance":
        raise InvalidSortingType("Invalid sorting type has given")

    if "saved" in programMode:
        print(
            "saved posts\nuser:{username}\nlimit={limit}\n".format(
                username=reddit.user.me(),
                limit=programMode["limit"]
            ).upper(),noPrint=True
        )
        return extractDetails(reddit.user.me().saved(limit=programMode["limit"]))

    if "subreddit" in programMode:

        if programMode["subreddit"] == "frontpage":

            print (
                "subreddit: {subreddit}\nsort: {sort}\n" \
                "time: {time}\nlimit: {limit}\n".format(
                    limit=programMode["limit"],
                    sort=programMode["sort"],
                    subreddit=programMode["subreddit"],
                    time=programMode["time"]
                ).upper(),noPrint=True
            )
            return extractDetails(
                getattr(reddit.front,programMode["sort"]) (**keyword_params)
            )

        else:  
            print (
                "subreddit: {subreddit}\nsort: {sort}\n" \
                "time: {time}\nlimit: {limit}\n".format(
                    limit=programMode["limit"],
                    sort=programMode["sort"],
                    subreddit=programMode["subreddit"],
                    time=programMode["time"]
                ).upper(),noPrint=True
            )
            return extractDetails(
                getattr(
                    reddit.subreddit(programMode["subreddit"]),programMode["sort"]
                ) (**keyword_params)
            )

    elif "multireddit" in programMode:
        print (
            "user: {user}\n" \
            "multireddit: {multireddit}\nsort: {sort}\n" \
            "time: {time}\nlimit: {limit}\n".format(
                user=programMode["user"],
                limit=programMode["limit"],
                sort=programMode["sort"],
                multireddit=programMode["multireddit"],
                time=programMode["time"]
            ).upper(),noPrint=True
        )
        try:
            return extractDetails(
                getattr(
                    reddit.multireddit(
                        programMode["user"], programMode["multireddit"]
                    ),programMode["sort"]
                ) (**keyword_params)
            )
        except NotFound:
            raise MultiredditNotFound("Multireddit not found")

    elif "submitted" in programMode:
        print (
            "submitted posts of {user}\nsort: {sort}\n" \
            "time: {time}\nlimit: {limit}\n".format(
                limit=programMode["limit"],
                sort=programMode["sort"],
                user=programMode["user"],
                time=programMode["time"]
            ).upper(),noPrint=True
        )
        return extractDetails(
            getattr(
                reddit.redditor(programMode["user"]).submissions,programMode["sort"]
            ) (**keyword_params)
        )

    elif "upvoted" in programMode:
        print (
            "upvoted posts of {user}\nlimit: {limit}\n".format(
                user=programMode["user"],
                limit=programMode["limit"]
            ).upper(),noPrint=True
        )
        try:
            return extractDetails(
                reddit.redditor(programMode["user"]).upvoted(limit=programMode["limit"])
            )
        except Forbidden:
            raise InsufficientPermission("You do not have permission to do that")

    elif "post" in programMode:
        print("post: {post}\n".format(post=programMode["post"]).upper(),noPrint=True)
        return extractDetails(
            reddit.submission(url=programMode["post"]),SINGLE_POST=True
        )

def extractDetails(posts,SINGLE_POST=False):
    """Check posts and decide if it can be downloaded.
    If so, create a dictionary with post details and append them to a list.
    Write all of posts to file. Return the list
    """

    postList = []
    postCount = 1

    allPosts = {}

    print("\nGETTING POSTS")
    postsFile = createLogFile("POSTS")

    if SINGLE_POST:
        submission = posts
        postCount += 1 
        try:
            details = {'POSTID':submission.id,
                       'TITLE':submission.title,
                       'REDDITOR':str(submission.author),
                       'TYPE':None,
                       'CONTENTURL':submission.url,
                       'SUBREDDIT':submission.subreddit.display_name,
                       'UPVOTES': submission.score,
                       'FLAIR':submission.link_flair_text,
                       'DATE':str(time.strftime(
                                      "%Y-%m-%d_%H-%M",
                                      time.localtime(submission.created_utc)
                                      ))}
            if 'gallery' in submission.url:
                details['CONTENTURL'] = genLinksifGallery(submission.media_metadata)
        except AttributeError:
            pass

        if not any(domain in submission.domain for domain in GLOBAL.arguments.skip_domain):
            result = matchWithDownloader(submission)

            if result is not None:
                details = {**details, **result}
                postList.append(details)
                postsFile.add({postCount:details})

    else:
        try:
            for submission in posts:
                
                if postCount % 100 == 0:
                    sys.stdout.write("• ")
                    sys.stdout.flush()

                if postCount % 1000 == 0:
                    sys.stdout.write("\n"+" "*14)
                    sys.stdout.flush()

                try:
                    details = {'POSTID':submission.id,
                            'TITLE':submission.title,
                            'REDDITOR':str(submission.author),
                            'TYPE':None,
                            'CONTENTURL':submission.url,
                            'SUBREDDIT':submission.subreddit.display_name,
                            'UPVOTES': submission.score,
                            'FLAIR':submission.link_flair_text,
                            'DATE':str(time.strftime(
                                      "%Y-%m-%d_%H-%M",
                                      time.localtime(submission.created_utc)
                                      ))}
                    if 'gallery' in submission.url:
                        details['CONTENTURL'] = genLinksifGallery(submission.media_metadata)
                except AttributeError:
                    continue

                if details['POSTID'] in GLOBAL.downloadedPosts(): continue

                if not any(domain in submission.domain for domain in GLOBAL.arguments.skip_domain):
                    result = matchWithDownloader(submission)

                    if result is not None:
                        details = {**details, **result}
                        postList.append(details)
                    
                    allPosts[postCount] = details
                    postCount += 1
                
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt",noPrint=True)
        
        postsFile.add(allPosts)

    if not len(postList) == 0:
        print()
        return postList
    else:
        raise NoMatchingSubmissionFound("No matching submission was found")

def matchWithDownloader(submission):

    if 'gallery' in submission.url:
        return{'TYPE':'gallery'}
        
    directLink = extractDirectLink(submission.url)
    if directLink:
         return {'TYPE': 'direct',
                 'CONTENTURL': directLink}

    if 'v.redd.it' in submission.domain:
        bitrates = ["DASH_1080","DASH_720","DASH_600", \
                    "DASH_480","DASH_360","DASH_240"]
                    
        for bitrate in bitrates:
            videoURL = submission.url+"/"+bitrate+".mp4"

            try:    
                responseCode = urllib.request.urlopen(videoURL).getcode()
            except urllib.error.HTTPError:
                responseCode = 0

            if responseCode == 200:
                return {'TYPE': 'v.redd.it', 'CONTENTURL': videoURL}    

    if 'gfycat' in submission.domain:
        return {'TYPE': 'gfycat'}

    if 'youtube' in submission.domain \
        and 'watch' in submission.url:
        return {'TYPE': 'youtube'}

    if 'youtu.be' in submission.domain:
        url = urllib.request.urlopen(submission.url).geturl()
        if 'watch' in url:
            return {'TYPE': 'youtube'}

    elif 'imgur' in submission.domain:
        return {'TYPE': 'imgur'}

    elif 'erome' in submission.domain:
        return {'TYPE': 'erome'}

    elif 'redgifs' in submission.domain:
        return {'TYPE': 'redgifs'}

    elif 'gifdeliverynetwork' in submission.domain:
        return {'TYPE': 'gifdeliverynetwork'}

    if 'reddit.com/gallery' in submission.url:
        return {'TYPE': 'gallery'}
      
    elif submission.is_self and 'self' not in GLOBAL.arguments.skip:
        return {'TYPE': 'self',
                'CONTENT': submission.selftext}

def extractDirectLink(URL):
    """Check if link is a direct image link.
    If so, return URL,
    if not, return False
    """

    imageTypes = ['jpg','jpeg','png','mp4','webm','gif']
    if URL[-1] == "/":
        URL = URL[:-1]

    if "i.reddituploads.com" in URL:
        return URL

    for extension in imageTypes:
        if extension == URL.split(".")[-1]:
            return URL
    else:
        return  None

def genLinksifGallery(metadata):
    galleryImgUrls = list()
    for key in metadata:
        galleryImgUrls.append(metadata[key]['s']['u'].split('?')[0].replace('preview','i'))
    return galleryImgUrls