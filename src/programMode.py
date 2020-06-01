from src.errors import SearchModeError, RedditorNameError, ProgramModeError, InvalidSortingType
from src.utils import GLOBAL
from src.parser import LinkDesigner
from pathlib import Path
import sys

class ProgramMode:

    def __init__(self,arguments):
        self.arguments = arguments

    def generate(self):

        try:
            self._validateProgramMode()
        except ProgramModeError:
            self._promptUser()

        programMode = {}

        if self.arguments.user is not None:
            programMode["user"] = self.arguments.user

        if self.arguments.search is not None:
            programMode["search"] = self.arguments.search
            if self.arguments.sort == "hot" or \
            self.arguments.sort == "controversial" or \
            self.arguments.sort == "rising":
                self.arguments.sort = "relevance"

        if self.arguments.sort is not None:
            programMode["sort"] = self.arguments.sort
        else:
            if self.arguments.submitted:
                programMode["sort"] = "new"
            else:
                programMode["sort"] = "hot"

        if self.arguments.time is not None:
            programMode["time"] = self.arguments.time
        else:
            programMode["time"] = "all"

        if self.arguments.link is not None:

            self.arguments.link = self.arguments.link.strip("\"")

            programMode = LinkDesigner(self.arguments.link)

            if self.arguments.search is not None:
                programMode["search"] = self.arguments.search

            if self.arguments.sort is not None:
                programMode["sort"] = self.arguments.sort

            if self.arguments.time is not None:
                programMode["time"] = self.arguments.time

        elif self.arguments.subreddit is not None:
            if type(self.arguments.subreddit) == list:    
                self.arguments.subreddit = "+".join(self.arguments.subreddit)

            programMode["subreddit"] = self.arguments.subreddit

        elif self.arguments.multireddit is not None:
            programMode["multireddit"] = self.arguments.multireddit

        elif self.arguments.saved is True:
            programMode["saved"] = True

        elif self.arguments.upvoted is True:
            programMode["upvoted"] = True

        elif self.arguments.submitted is not None:
            programMode["submitted"] = True

            if self.arguments.sort == "rising":
                raise InvalidSortingType("Invalid sorting type has given")
        
        programMode["limit"] = self.arguments.limit

        return programMode

    @staticmethod
    def _chooseFrom(choices):
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
            input("> ")

        if choice == "0" or choice == "exit":
            sys.exit()
        elif choice in choicesByIndex:
            return choices[int(choice)-1]
        else:
            return choice

    def _promptUser(self):
        print("select program mode:")
        programModes = [
            "search","subreddit","multireddit",
            "submitted","upvoted","saved","log"
        ]
        programMode = self._chooseFrom(programModes)

        if programMode == "search":
            self.arguments.search = input("\nquery: ")
            self.arguments.subreddit = input("\nsubreddit: ")

            print("\nselect sort type:")
            sortTypes = [
                "relevance","top","new"
            ]
            sortType = self._chooseFrom(sortTypes)
            self.arguments.sort = sortType

            print("\nselect time filter:")
            timeFilters = [
                "hour","day","week","month","year","all"
            ]
            timeFilter = self._chooseFrom(timeFilters)
            self.arguments.time = timeFilter

        if programMode == "subreddit":

            subredditInput = input("(type frontpage for all subscribed subreddits,\n" \
                                   " use plus to seperate multi subreddits:" \
                                   " pics+funny+me_irl etc.)\n\n" \
                                   "subreddit: ")
            self.arguments.subreddit = subredditInput

            # while not (subredditInput == "" or subredditInput.lower() == "frontpage"):
            #     subredditInput = input("subreddit: ")
            #     self.arguments.subreddit += "+" + subredditInput

            if " " in self.arguments.subreddit:
                self.arguments.subreddit = "+".join(self.arguments.subreddit.split())

            # DELETE THE PLUS (+) AT THE END
            if not subredditInput.lower() == "frontpage" \
                and self.arguments.subreddit[-1] == "+":
                self.arguments.subreddit = self.arguments.subreddit[:-1]

            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","rising","controversial"
            ]
            sortType = self._chooseFrom(sortTypes)
            self.arguments.sort = sortType

            if sortType in ["top","controversial"]:
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self._chooseFrom(timeFilters)
                self.arguments.time = timeFilter
            else:
                self.arguments.time = "all"

        elif programMode == "multireddit":
            self.arguments.user = input("\nmultireddit owner: ")
            self.arguments.multireddit = input("\nmultireddit: ")
            
            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","rising","controversial"
            ]
            sortType = self._chooseFrom(sortTypes)
            self.arguments.sort = sortType

            if sortType in ["top","controversial"]:
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self._chooseFrom(timeFilters)
                self.arguments.time = timeFilter
            else:
                self.arguments.time = "all"
        
        elif programMode == "submitted":
            self.arguments.submitted = True
            self.arguments.user = input("\nredditor: ")

            print("\nselect sort type:")
            sortTypes = [
                "hot","top","new","controversial"
            ]
            sortType = self._chooseFrom(sortTypes)
            self.arguments.sort = sortType

            if sortType == "top":
                print("\nselect time filter:")
                timeFilters = [
                    "hour","day","week","month","year","all"
                ]
                timeFilter = self._chooseFrom(timeFilters)
                self.arguments.time = timeFilter
            else:
                self.arguments.time = "all"
        
        elif programMode == "upvoted":
            self.arguments.upvoted = True
            self.arguments.user = input("\nredditor: ")
        
        elif programMode == "saved":
            self.arguments.saved = True
        
        elif programMode == "log":
            while True:
                self.arguments.log = input("\nlog file directory:")
                if Path(self.arguments.log).is_file():
                    break 
        while True:
            try:
                self.arguments.limit = int(input("\nlimit (0 for none): "))
                if self.arguments.limit == 0:
                    self.arguments.limit = None
                break
            except ValueError:
                pass

    def _validateProgramMode(self):
        """Check if command-line self.arguments are given correcly,
        if not, raise errors
        """

        if self.arguments.user is None:
            user = 0
        else:
            user = 1

        search = 1 if self.arguments.search else 0

        modes = [
            "saved","subreddit","submitted","log","link","upvoted","multireddit"
        ]

        values = {
            x: 0 if getattr(self.arguments,x) is None or \
                    getattr(self.arguments,x) is False \
                else 1 \
                for x in modes
        }

        if not sum(values[x] for x in values) == 1:
            raise ProgramModeError("Invalid program mode")
        
        if search+values["saved"] == 2:
            raise SearchModeError("You cannot search in your saved posts")

        if search+values["submitted"] == 2:
            raise SearchModeError("You cannot search in submitted posts")

        if search+values["upvoted"] == 2:
            raise SearchModeError("You cannot search in upvoted posts")

        if search+values["log"] == 2:
            raise SearchModeError("You cannot search in log files")

        if values["upvoted"]+values["submitted"] == 1 and user == 0:
            raise RedditorNameError("No redditor name given")
