import sys
import time
import urllib.request
from urllib.error import HTTPError

from prawcore.exceptions import Forbidden, NotFound

from bulkredditdownloader.errors import (InsufficientPermission, InvalidSortingType, MultiredditNotFound, NoMatchingSubmissionFound,
                                         NoPrawSupport)
from bulkredditdownloader.reddit import Reddit
from praw.models.listing.generator import ListingGenerator
from bulkredditdownloader.utils import GLOBAL, createLogFile, printToFile
from praw.models import Submission

print = printToFile


def getPosts(program_mode: dict) -> list[dict]:
    """Call PRAW regarding to arguments and pass it to extractDetails.
    Return what extractDetails has returned.
    """
    reddit = Reddit(GLOBAL.config["credentials"]["reddit"]).begin()

    if program_mode["sort"] == "best":
        raise NoPrawSupport("PRAW does not support that")

    if "subreddit" in program_mode:
        if "search" in program_mode:
            if program_mode["subreddit"] == "frontpage":
                program_mode["subreddit"] = "all"

    if "user" in program_mode:
        if program_mode["user"] == "me":
            program_mode["user"] = str(reddit.user.me())

    if "search" not in program_mode:
        if program_mode["sort"] == "top" or program_mode["sort"] == "controversial":
            keyword_params = {"time_filter": program_mode["time"], "limit": program_mode["limit"]}
        # OTHER SORT TYPES DON'T TAKE TIME_FILTER
        else:
            keyword_params = {"limit": program_mode["limit"]}
    else:
        keyword_params = {"time_filter": program_mode["time"], "limit": program_mode["limit"]}

    if "search" in program_mode:
        if program_mode["sort"] in ["hot", "rising", "controversial"]:
            raise InvalidSortingType("Invalid sorting type has given")

        if "subreddit" in program_mode:
            print(
                "search for \"{search}\" in\n"
                "subreddit: {subreddit}\nsort: {sort}\n"
                "time: {time}\nlimit: {limit}\n".format(
                    search=program_mode["search"],
                    limit=program_mode["limit"],
                    sort=program_mode["sort"],
                    subreddit=program_mode["subreddit"],
                    time=program_mode["time"]
                ).upper(), no_print=True
            )
            return extractDetails(
                reddit.subreddit(program_mode["subreddit"]).search(
                    program_mode["search"],
                    limit=program_mode["limit"],
                    sort=program_mode["sort"],
                    time_filter=program_mode["time"]
                )
            )

        elif "multireddit" in program_mode:
            raise NoPrawSupport("PRAW does not support that")

        elif "user" in program_mode:
            raise NoPrawSupport("PRAW does not support that")

        elif "saved" in program_mode:
            raise ("Reddit does not support that")

    if program_mode["sort"] == "relevance":
        raise InvalidSortingType("Invalid sorting type has given")

    if "saved" in program_mode:
        print("saved posts\nuser:{username}\nlimit={limit}\n".format(
            username=reddit.user.me(),
            limit=program_mode["limit"]).upper(),
            no_print=True
        )
        return extractDetails(reddit.user.me().saved(limit=program_mode["limit"]))

    if "subreddit" in program_mode:

        if program_mode["subreddit"] == "frontpage":
            print(
                "subreddit: {subreddit}\nsort: {sort}\n"
                "time: {time}\nlimit: {limit}\n".format(
                    limit=program_mode["limit"],
                    sort=program_mode["sort"],
                    subreddit=program_mode["subreddit"],
                    time=program_mode["time"]).upper(),
                no_print=True
            )
            return extractDetails(getattr(reddit.front, program_mode["sort"])(**keyword_params))

        else:
            print(
                "subreddit: {subreddit}\nsort: {sort}\n"
                "time: {time}\nlimit: {limit}\n".format(
                    limit=program_mode["limit"],
                    sort=program_mode["sort"],
                    subreddit=program_mode["subreddit"],
                    time=program_mode["time"]).upper(),
                no_print=True
            )
            return extractDetails(
                getattr(reddit.subreddit(program_mode["subreddit"]), program_mode["sort"])(**keyword_params)
            )
        print(
            "subreddit: {subreddit}\nsort: {sort}\n"
            "time: {time}\nlimit: {limit}\n".format(
                limit=programMode["limit"],
                sort=programMode["sort"],
                subreddit=programMode["subreddit"],
                time=programMode["time"]
            ).upper(), noPrint=True
        )
        return extractDetails(
            getattr(
                reddit.subreddit(programMode["subreddit"]), programMode["sort"]
            )(**keyword_params)
        )

    elif "multireddit" in program_mode:
        print(
            "user: {user}\n"
            "multireddit: {multireddit}\nsort: {sort}\n"
            "time: {time}\nlimit: {limit}\n".format(
                user=program_mode["user"],
                limit=program_mode["limit"],
                sort=program_mode["sort"],
                multireddit=program_mode["multireddit"],
                time=program_mode["time"]).upper(),
            no_print=True
        )
        try:
            return extractDetails(
                getattr(reddit.multireddit(program_mode["user"], program_mode["multireddit"]),
                        program_mode["sort"]
                        )(**keyword_params)
            )
        except NotFound:
            raise MultiredditNotFound("Multireddit not found")

    elif "submitted" in program_mode:
        print(
            "submitted posts of {user}\nsort: {sort}\n"
            "time: {time}\nlimit: {limit}\n".format(
                limit=program_mode["limit"],
                sort=program_mode["sort"],
                user=program_mode["user"],
                time=program_mode["time"]).upper(),
            no_print=True
        )
        return extractDetails(
            getattr(reddit.redditor(program_mode["user"]).submissions, program_mode["sort"])(**keyword_params)
        )

    elif "upvoted" in program_mode:
        print(
            "upvoted posts of {user}\nlimit: {limit}\n".format(
                user=program_mode["user"],
                limit=program_mode["limit"]).upper(),
            no_print=True
        )
        try:
            return extractDetails(reddit.redditor(program_mode["user"]).upvoted(limit=program_mode["limit"]))
        except Forbidden:
            raise InsufficientPermission(
                "You do not have permission to do that")

    elif "post" in program_mode:
        print("post: {post}\n".format(post=program_mode["post"]).upper(), no_print=True)
        return extractDetails(reddit.submission(url=program_mode["post"]), single_post=True)


def extractDetails(posts: (ListingGenerator, Submission), single_post=False) -> list[dict]:
    """Check posts and decide if it can be downloaded.
    If so, create a dictionary with post details and append them to a list.
    Write all of posts to file. Return the list
    """
    post_list = []
    post_count = 1

    all_posts = {}

    print("\nGETTING POSTS")
    posts_file = createLogFile("POSTS")

    if single_post:
        submission = posts
        post_count += 1
        try:
            details = {'POSTID': submission.id,
                       'TITLE': submission.title,
                       'REDDITOR': str(submission.author),
                       'TYPE': None,
                       'CONTENTURL': submission.url,
                       'SUBREDDIT': submission.subreddit.display_name,
                       'UPVOTES': submission.score,
                       'FLAIR': submission.link_flair_text,
                       'DATE': str(time.strftime("%Y-%m-%d_%H-%M", time.localtime(submission.created_utc)))
                       }
        except AttributeError:
            pass

        if not any(
                domain in submission.domain for domain in GLOBAL.arguments.skip_domain):
            result = matchWithDownloader(submission)

            if result is not None:
                details = {**details, **result}
                post_list.append(details)
                posts_file.add({post_count: details})

    else:
        try:
            for submission in posts:
                if post_count % 100 == 0:
                    sys.stdout.write("• ")
                    sys.stdout.flush()

                if post_count % 1000 == 0:
                    sys.stdout.write("\n" + " " * 14)
                    sys.stdout.flush()

                try:
                    details = {'POSTID': submission.id,
                               'TITLE': submission.title,
                               'REDDITOR': str(submission.author),
                               'TYPE': None,
                               'CONTENTURL': submission.url,
                               'SUBREDDIT': submission.subreddit.display_name,
                               'UPVOTES': submission.score,
                               'FLAIR': submission.link_flair_text,
                               'DATE': str(time.strftime("%Y-%m-%d_%H-%M", time.localtime(submission.created_utc)))
                               }
                except AttributeError:
                    continue

                if details['POSTID'] in GLOBAL.downloadedPosts():
                    continue

                if not any(
                        domain in submission.domain for domain in GLOBAL.arguments.skip_domain):
                    result = matchWithDownloader(submission)

                    if result is not None:
                        details = {**details, **result}
                        post_list.append(details)

                    all_posts[post_count] = details
                    post_count += 1

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt", no_print=True)

        posts_file.add(all_posts)

    if not len(post_list) == 0:
        print()
        return post_list
    else:
        raise NoMatchingSubmissionFound("No matching submission was found")


def matchWithDownloader(submission: Submission) -> dict[str, str]:
    direct_link = extractDirectLink(submission.url)
    if direct_link:
        return {'TYPE': 'direct', 'CONTENTURL': direct_link}

    if 'v.redd.it' in submission.domain:
        bitrates = ["DASH_1080", "DASH_720", "DASH_600", "DASH_480", "DASH_360", "DASH_240"]

        for bitrate in bitrates:
            video_url = submission.url + "/" + bitrate + ".mp4"

            try:
                response_code = urllib.request.urlopen(video_url).getcode()
            except urllib.error.HTTPError:
                response_code = 0

            if response_code == 200:
                return {'TYPE': 'v.redd.it', 'CONTENTURL': video_url}

    if 'gfycat' in submission.domain:
        return {'TYPE': 'gfycat'}

    if 'youtube' in submission.domain and 'watch' in submission.url:
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


def extractDirectLink(url: str) -> (bool, str):
    """Check if link is a direct image link.
    If so, return URL,
    if not, return False
    """
    image_types = ['jpg', 'jpeg', 'png', 'mp4', 'webm', 'gif']
    if url[-1] == "/":
        url = url[:-1]

    if "i.reddituploads.com" in url:
        return url

    for extension in image_types:
        if extension == url.split(".")[-1]:
            return url
    else:
        return None
