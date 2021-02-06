from pprint import pprint

try:
    from src.errors import InvalidRedditLink
except ModuleNotFoundError:
    from errors import InvalidRedditLink


def QueryParser(passed_queries, index):
    extracted_queries = {}

    question_mark_index = passed_queries.index("?")
    header = passed_queries[:question_mark_index]
    extracted_queries["HEADER"] = header
    queries = passed_queries[question_mark_index + 1:]

    parsed_queries = queries.split("&")

    for query in parsed_queries:
        query = query.split("=")
        extracted_queries[query[0]] = query[1]

    if extracted_queries["HEADER"] == "search":
        extracted_queries["q"] = extracted_queries["q"].replace("%20", " ")

    return extracted_queries


def LinkParser(link):
    result = {}
    short_link = False

    if "reddit.com" not in link:
        raise InvalidRedditLink("Invalid reddit link")

    splitted_link = link.split("/")

    if splitted_link[0] == "https:" or splitted_link[0] == "http:":
        splitted_link = splitted_link[2:]

    try:
        if (splitted_link[-2].endswith("reddit.com") and
                splitted_link[-1] == "") or splitted_link[-1].endswith("reddit.com"):

            result["sort"] = "best"
            return result
    except IndexError:
        if splitted_link[0].endswith("reddit.com"):
            result["sort"] = "best"
            return result

    if "redd.it" in splitted_link:
        short_link = True

    if splitted_link[0].endswith("reddit.com"):
        splitted_link = splitted_link[1:]

    if "comments" in splitted_link:
        result = {"post": link}
        return result

    elif "me" in splitted_link or \
         "u" in splitted_link or \
         "user" in splitted_link or \
         "r" in splitted_link or \
         "m" in splitted_link:

        if "r" in splitted_link:
            result["subreddit"] = splitted_link[splitted_link.index("r") + 1]

        elif "m" in splitted_link:
            result["multireddit"] = splitted_link[splitted_link.index("m") + 1]
            result["user"] = splitted_link[splitted_link.index("m") - 1]

        else:
            for index in range(len(splitted_link)):
                if splitted_link[index] == "u" or splitted_link[index] == "user":
                    result["user"] = splitted_link[index + 1]

                elif splitted_link[index] == "me":
                    result["user"] = "me"

    for index in range(len(splitted_link)):
        if splitted_link[index] in [
            "hot", "top", "new", "controversial", "rising"
        ]:

            result["sort"] = splitted_link[index]

            if index == 0:
                result["subreddit"] = "frontpage"

        elif splitted_link[index] in ["submitted", "saved", "posts", "upvoted"]:
            if splitted_link[index] == "submitted" or splitted_link[index] == "posts":
                result["submitted"] = {}

            elif splitted_link[index] == "saved":
                result["saved"] = True

            elif splitted_link[index] == "upvoted":
                result["upvoted"] = True

        elif "?" in splitted_link[index]:
            parsed_query = QueryParser(splitted_link[index], index)
            if parsed_query["HEADER"] == "search":
                del parsed_query["HEADER"]
                result["search"] = parsed_query

            elif parsed_query["HEADER"] == "submitted" or \
                    parsed_query["HEADER"] == "posts":
                del parsed_query["HEADER"]
                result["submitted"] = parsed_query

            else:
                del parsed_query["HEADER"]
                result["queries"] = parsed_query

    if not ("upvoted" in result or
            "saved" in result or
            "submitted" in result or
            "multireddit" in result) and "user" in result:
        result["submitted"] = {}

    return result


def LinkDesigner(link):
    attributes = LinkParser(link)
    mode = {}

    if "post" in attributes:
        mode["post"] = attributes["post"]
        mode["sort"] = ""
        mode["time"] = ""
        return mode

    elif "search" in attributes:
        mode["search"] = attributes["search"]["q"]

        if "restrict_sr" in attributes["search"]:

            if not (attributes["search"]["restrict_sr"] == 0 or
                    attributes["search"]["restrict_sr"] == "off" or
                    attributes["search"]["restrict_sr"] == ""):

                if "subreddit" in attributes:
                    mode["subreddit"] = attributes["subreddit"]
                elif "multireddit" in attributes:
                    mode["multreddit"] = attributes["multireddit"]
                    mode["user"] = attributes["user"]
            else:
                mode["subreddit"] = "all"
        else:
            mode["subreddit"] = "all"

        if "t" in attributes["search"]:
            mode["time"] = attributes["search"]["t"]
        else:
            mode["time"] = "all"

        if "sort" in attributes["search"]:
            mode["sort"] = attributes["search"]["sort"]
        else:
            mode["sort"] = "relevance"

        if "include_over_18" in attributes["search"]:
            if attributes["search"]["include_over_18"] == 1 or attributes["search"]["include_over_18"] == "on":
                mode["nsfw"] = True
            else:
                mode["nsfw"] = False

    else:
        if "queries" in attributes:
            if not ("submitted" in attributes or "posts" in attributes):

                if "t" in attributes["queries"]:
                    mode["time"] = attributes["queries"]["t"]
                else:
                    mode["time"] = "day"
            else:
                if "t" in attributes["queries"]:
                    mode["time"] = attributes["queries"]["t"]
                else:
                    mode["time"] = "all"

                if "sort" in attributes["queries"]:
                    mode["sort"] = attributes["queries"]["sort"]
                else:
                    mode["sort"] = "new"
        else:
            mode["time"] = "day"

    if "subreddit" in attributes and "search" not in attributes:
        mode["subreddit"] = attributes["subreddit"]

    elif "user" in attributes and "search" not in attributes:
        mode["user"] = attributes["user"]

        if "submitted" in attributes:
            mode["submitted"] = True
            if "sort" in attributes["submitted"]:
                mode["sort"] = attributes["submitted"]["sort"]
            elif "sort" in mode:
                pass
            else:
                mode["sort"] = "new"

            if "t" in attributes["submitted"]:
                mode["time"] = attributes["submitted"]["t"]
            else:
                mode["time"] = "all"

        elif "saved" in attributes:
            mode["saved"] = True

        elif "upvoted" in attributes:
            mode["upvoted"] = True

        elif "multireddit" in attributes:
            mode["multireddit"] = attributes["multireddit"]

    if "sort" in attributes:
        mode["sort"] = attributes["sort"]
    elif "sort" in mode:
        pass
    else:
        mode["sort"] = "hot"

    return mode



if __name__ == "__main__":
    while True:
        link = input("> ")
        pprint(LinkDesigner(link))
