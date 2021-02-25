import argparse
import sys


class Arguments:
    @staticmethod
    def parse(arguments=None):
        """Initialize argparse and add arguments"""
        if arguments is None:
            arguments = []

        parser = argparse.ArgumentParser(allow_abbrev=False,
                                         description="This program downloads "
                                         "media from reddit "
                                         "posts")
        parser.add_argument("--directory", "-d",
                            help="Specifies the directory where posts will be "
                            "downloaded to",
                            metavar="DIRECTORY")

        parser.add_argument("--verbose", "-v",
                            help="Verbose Mode",
                            action="store_true",
                            default=False)

        parser.add_argument("--quit", "-q",
                            help="Auto quit afer the process finishes",
                            action="store_true",
                            default=False)

        parser.add_argument("--link", "-l",
                            help="Get posts from link",
                            metavar="link")

        parser.add_argument("--saved",
                            action="store_true",
                            required="--unsave" in sys.argv,
                            help="Triggers saved mode")

        parser.add_argument("--unsave",
                            action="store_true",
                            help="Unsaves downloaded posts")

        parser.add_argument("--submitted",
                            action="store_true",
                            help="Gets posts of --user")

        parser.add_argument("--upvoted",
                            action="store_true",
                            help="Gets upvoted posts of --user")

        parser.add_argument("--log",
                            help="Takes a log file which created by itself "
                            "(json files), reads posts and tries downloadin"
                            "g them again.",
                            # type=argparse.FileType('r'),
                            metavar="LOG FILE")

        parser.add_argument(
            "--subreddit",
            nargs="+",
            help="Triggers subreddit mode and takes subreddit's "
            "name without r/. use \"frontpage\" for frontpage",
            metavar="SUBREDDIT",
            type=str)

        parser.add_argument("--multireddit",
                            help="Triggers multireddit mode and takes "
                            "multireddit's name without m/",
                            metavar="MULTIREDDIT",
                            type=str)

        parser.add_argument("--user",
                            help="reddit username if needed. use \"me\" for "
                            "current user",
                            required="--multireddit" in sys.argv or
                            "--submitted" in sys.argv,
                            metavar="redditor",
                            type=str)

        parser.add_argument(
            "--search",
            help="Searches for given query in given subreddits",
            metavar="query",
            type=str)

        parser.add_argument("--sort",
                            help="Either hot, top, new, controversial, rising "
                            "or relevance default: hot",
                            choices=[
                                "hot", "top", "new", "controversial", "rising",
                                "relevance"
                            ],
                            metavar="SORT TYPE",
                            type=str)

        parser.add_argument("--limit",
                            help="default: unlimited",
                            metavar="Limit",
                            type=int)

        parser.add_argument("--time",
                            help="Either hour, day, week, month, year or all."
                            " default: all",
                            choices=["all", "hour", "day",
                                     "week", "month", "year"],
                            metavar="TIME_LIMIT",
                            type=str)

        parser.add_argument("--skip",
                            nargs="+",
                            help="Skip posts with given type",
                            type=str,
                            choices=["images", "videos", "gifs", "self"],
                            default=[])

        parser.add_argument("--skip-domain",
                            nargs="+",
                            help="Skip posts with given domain",
                            type=str,
                            default=[])

        parser.add_argument("--set-folderpath",
                            action="store_true",
                            help="Set custom folderpath"
                            )

        parser.add_argument("--set-filename",
                            action="store_true",
                            help="Set custom filename",
                            )

        parser.add_argument(
            "--set-default-directory",
            action="store_true",
            help="Set a default directory to be used in case no directory is given",
        )

        parser.add_argument(
            "--set-default-options",
            action="store_true",
            help="Set default options to use everytime program runs",
        )

        parser.add_argument(
            "--use-local-config",
            action="store_true",
            help="Creates a config file in the program's directory and uses it. Useful for having multiple configs",
        )

        parser.add_argument(
            "--no-dupes",
            action="store_true",
            help="Do not download duplicate posts on different subreddits",
        )

        parser.add_argument(
            "--downloaded-posts",
            help="Use a hash file to keep track of downloaded files",
            type=str)

        parser.add_argument(
            "--no-download",
            action="store_true",
            help="Just saved posts into a the POSTS.json file without downloading")

        if arguments == []:
            return parser.parse_args()
        return parser.parse_args(arguments)
