import sys
from pathlib import Path

from bulkredditdownloader.errors import InvalidSortingType, ProgramModeError, RedditorNameError, SearchModeError
from bulkredditdownloader.parser import LinkDesigner
import argparse



class ProgramMode:

    def __init__(self, arguments: argparse.Namespace):
        self.arguments = arguments

    def generate(self) -> dict:
        try:
            self._validateProgramMode()
        except ProgramModeError:
            self._promptUser()

        program_mode = {}

        if self.arguments.user is not None:
            program_mode["user"] = self.arguments.user

        if self.arguments.search is not None:
            program_mode["search"] = self.arguments.search
            if self.arguments.sort == "hot" or \
                    self.arguments.sort == "controversial" or \
                    self.arguments.sort == "rising":
                self.arguments.sort = "relevance"

        if self.arguments.sort is not None:
            program_mode["sort"] = self.arguments.sort
        else:
            if self.arguments.submitted:
                program_mode["sort"] = "new"
            else:
                program_mode["sort"] = "hot"

        if self.arguments.time is not None:
            program_mode["time"] = self.arguments.time
        else:
            program_mode["time"] = "all"

        if self.arguments.link is not None:
            self.arguments.link = self.arguments.link.strip("\"")

            program_mode = LinkDesigner(self.arguments.link)

            if self.arguments.search is not None:
                program_mode["search"] = self.arguments.search

            if self.arguments.sort is not None:
                program_mode["sort"] = self.arguments.sort

            if self.arguments.time is not None:
                program_mode["time"] = self.arguments.time

        elif self.arguments.subreddit is not None:
            if isinstance(self.arguments.subreddit, list):
                self.arguments.subreddit = "+".join(self.arguments.subreddit)

            program_mode["subreddit"] = self.arguments.subreddit

        elif self.arguments.multireddit is not None:
            program_mode["multireddit"] = self.arguments.multireddit

        elif self.arguments.saved is True:
            program_mode["saved"] = True

        elif self.arguments.upvoted is True:
            program_mode["upvoted"] = True

        elif self.arguments.submitted is not None:
            program_mode["submitted"] = True

            if self.arguments.sort == "rising":
                raise InvalidSortingType("Invalid sorting type has given")

        program_mode["limit"] = self.arguments.limit

        return program_mode

    @staticmethod
    def _chooseFrom(choices: list[str]):
        print()
        choices_by_index = list(str(x) for x in range(len(choices) + 1))
        for i in range(len(choices)):
            print("{indent}[{order}] {mode}".format(indent=" " * 4, order=i + 1, mode=choices[i]))
        print(" " * 4 + "[0] exit\n")
        choice = input("> ")
        while not choice.lower() in choices + choices_by_index + ["exit"]:
            print("Invalid input\n")
            input("> ")

        if choice == "0" or choice == "exit":
            sys.exit()
        elif choice in choices_by_index:
            return choices[int(choice) - 1]
        else:
            return choice

    def _promptUser(self):
        print("select program mode:")
        program_modes = ["search", "subreddit", "multireddit", "submitted", "upvoted", "saved", "log"]
        program_mode = self._chooseFrom(program_modes)

        if program_mode == "search":
            self.arguments.search = input("\nquery: ")
            self.arguments.subreddit = input("\nsubreddit: ")

            print("\nselect sort type:")
            sort_types = ["relevance", "top", "new"]
            sort_type = self._chooseFrom(sort_types)
            self.arguments.sort = sort_type

            print("\nselect time filter:")
            time_filters = ["hour", "day", "week", "month", "year", "all"]
            time_filter = self._chooseFrom(time_filters)
            self.arguments.time = time_filter

        if program_mode == "subreddit":
            subreddit_input = input("(type frontpage for all subscribed subreddits,\n"
                                    " use plus to seperate multi subreddits:"
                                    " pics+funny+me_irl etc.)\n\n"
                                    "subreddit: ")
            self.arguments.subreddit = subreddit_input

            if " " in self.arguments.subreddit:
                self.arguments.subreddit = "+".join(
                    self.arguments.subreddit.split())

            # DELETE THE PLUS (+) AT THE END
            if not subreddit_input.lower() == "frontpage" and self.arguments.subreddit[-1] == "+":
                self.arguments.subreddit = self.arguments.subreddit[:-1]

            print("\nselect sort type:")
            sort_types = ["hot", "top", "new", "rising", "controversial"]
            sort_type = self._chooseFrom(sort_types)
            self.arguments.sort = sort_type

            if sort_type in ["top", "controversial"]:
                print("\nselect time filter:")
                time_filters = ["hour", "day", "week", "month", "year", "all"]
                time_filter = self._chooseFrom(time_filters)
                self.arguments.time = time_filter
            else:
                self.arguments.time = "all"

        elif program_mode == "multireddit":
            self.arguments.user = input("\nmultireddit owner: ")
            self.arguments.multireddit = input("\nmultireddit: ")

            print("\nselect sort type:")
            sort_types = ["hot", "top", "new", "rising", "controversial"]
            sort_type = self._chooseFrom(sort_types)
            self.arguments.sort = sort_type

            if sort_type in ["top", "controversial"]:
                print("\nselect time filter:")
                time_filters = ["hour", "day", "week", "month", "year", "all"]
                time_filter = self._chooseFrom(time_filters)
                self.arguments.time = time_filter
            else:
                self.arguments.time = "all"

        elif program_mode == "submitted":
            self.arguments.submitted = True
            self.arguments.user = input("\nredditor: ")

            print("\nselect sort type:")
            sort_types = ["hot", "top", "new", "controversial"]
            sort_type = self._chooseFrom(sort_types)
            self.arguments.sort = sort_type

            if sort_type == "top":
                print("\nselect time filter:")
                time_filters = ["hour", "day", "week", "month", "year", "all"]
                time_filter = self._chooseFrom(time_filters)
                self.arguments.time = time_filter
            else:
                self.arguments.time = "all"

        elif program_mode == "upvoted":
            self.arguments.upvoted = True
            self.arguments.user = input("\nredditor: ")

        elif program_mode == "saved":
            self.arguments.saved = True

        elif program_mode == "log":
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

        modes = ["saved", "subreddit", "submitted", "log", "link", "upvoted", "multireddit"]

        values = {x: 0 if getattr(self.arguments, x) is None or
                  getattr(self.arguments, x) is False
                  else 1
                  for x in modes
                  }

        if not sum(values[x] for x in values) == 1:
            raise ProgramModeError("Invalid program mode")

        if search + values["saved"] == 2:
            raise SearchModeError("You cannot search in your saved posts")

        if search + values["submitted"] == 2:
            raise SearchModeError("You cannot search in submitted posts")

        if search + values["upvoted"] == 2:
            raise SearchModeError("You cannot search in upvoted posts")

        if search + values["log"] == 2:
            raise SearchModeError("You cannot search in log files")

        if values["upvoted"] + values["submitted"] == 1 and user == 0:
            raise RedditorNameError("No redditor name given")
