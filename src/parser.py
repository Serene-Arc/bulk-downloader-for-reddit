from pprint import pprint

try:
    from src.errors import InvalidRedditLink
except ModuleNotFoundError:
    from errors import InvalidRedditLink

def QueryParser(PassedQueries,index):
    ExtractedQueries = {}

    QuestionMarkIndex = PassedQueries.index("?")
    Header = PassedQueries[:QuestionMarkIndex]
    ExtractedQueries["HEADER"] = Header
    Queries = PassedQueries[QuestionMarkIndex+1:]

    ParsedQueries = Queries.split("&")

    for Query in ParsedQueries:
        Query = Query.split("=")
        ExtractedQueries[Query[0]] = Query[1]

    if ExtractedQueries["HEADER"] == "search":
        ExtractedQueries["q"] = ExtractedQueries["q"].replace("%20"," ")

    return ExtractedQueries

def LinkParser(LINK):
    RESULT = {}
    ShortLink = False

    if not "reddit.com" in LINK:
        raise InvalidRedditLink("Invalid reddit link")

    SplittedLink = LINK.split("/")

    if SplittedLink[0] == "https:" or SplittedLink[0] == "http:":
        SplittedLink = SplittedLink[2:]

    try:
        if (SplittedLink[-2].endswith("reddit.com") and \
            SplittedLink[-1] == "") or \
           SplittedLink[-1].endswith("reddit.com"):

            RESULT["sort"] = "best"
            return RESULT
    except IndexError:
        if SplittedLink[0].endswith("reddit.com"):
            RESULT["sort"] = "best"
            return RESULT

    if "redd.it" in SplittedLink:
        ShortLink = True

    if SplittedLink[0].endswith("reddit.com"):
        SplittedLink = SplittedLink[1:]
    
    if "comments" in SplittedLink:
        RESULT = {"post":LINK}
        return RESULT
    
    elif "me" in SplittedLink or \
         "u" in SplittedLink or \
         "user" in SplittedLink or \
         "r" in SplittedLink or \
         "m" in SplittedLink:

        if "r" in SplittedLink:
            RESULT["subreddit"] = SplittedLink[SplittedLink.index("r") + 1]

        elif "m" in SplittedLink:
            RESULT["multireddit"] = SplittedLink[SplittedLink.index("m") + 1]
            RESULT["user"] = SplittedLink[SplittedLink.index("m") - 1]
        
        else:
            for index in range(len(SplittedLink)):
                if SplittedLink[index] == "u" or \
                   SplittedLink[index] == "user":

                    RESULT["user"] = SplittedLink[index+1]

                elif SplittedLink[index] == "me":
                    RESULT["user"] = "me"


    for index in range(len(SplittedLink)):
        if SplittedLink[index] in [
            "hot","top","new","controversial","rising"
            ]:

            RESULT["sort"] = SplittedLink[index]

            if index == 0:
                RESULT["subreddit"] = "frontpage"
        
        elif SplittedLink[index] in ["submitted","saved","posts","upvoted"]:
            if SplittedLink[index] == "submitted" or \
               SplittedLink[index] == "posts":
                RESULT["submitted"] = {}

            elif SplittedLink[index] == "saved":
                RESULT["saved"] = True
            
            elif SplittedLink[index] == "upvoted":
                RESULT["upvoted"] = True

        elif "?" in SplittedLink[index]:
            ParsedQuery = QueryParser(SplittedLink[index],index)
            if ParsedQuery["HEADER"] == "search":
                del ParsedQuery["HEADER"]
                RESULT["search"] = ParsedQuery

            elif ParsedQuery["HEADER"] == "submitted" or \
                 ParsedQuery["HEADER"] == "posts":
                del ParsedQuery["HEADER"]
                RESULT["submitted"] = ParsedQuery

            else:
                del ParsedQuery["HEADER"]
                RESULT["queries"] = ParsedQuery

    if not ("upvoted" in RESULT or \
            "saved" in RESULT or \
            "submitted" in RESULT or \
            "multireddit" in RESULT) and \
       "user" in RESULT:
        RESULT["submitted"] = {}

    return RESULT

def LinkDesigner(LINK):

    attributes = LinkParser(LINK)
    MODE = {}

    if "post" in attributes:
        MODE["post"] = attributes["post"]
        MODE["sort"] = ""
        MODE["time"] = ""
        return MODE

    elif "search" in attributes:
        MODE["search"] = attributes["search"]["q"]

        if "restrict_sr" in attributes["search"]:
            
            if not (attributes["search"]["restrict_sr"] == 0 or \
                    attributes["search"]["restrict_sr"] == "off" or \
                    attributes["search"]["restrict_sr"] == ""):

                if "subreddit" in attributes:
                    MODE["subreddit"] = attributes["subreddit"]
                elif "multireddit" in attributes:
                    MODE["multreddit"] = attributes["multireddit"]
                    MODE["user"] = attributes["user"]
            else:
                MODE["subreddit"] = "all"
        else:
            MODE["subreddit"] = "all"

        if "t" in attributes["search"]:
            MODE["time"] = attributes["search"]["t"]
        else:
            MODE["time"] = "all"

        if "sort" in attributes["search"]:
            MODE["sort"] = attributes["search"]["sort"]
        else:
            MODE["sort"] = "relevance"
        
        if "include_over_18" in attributes["search"]:
            if attributes["search"]["include_over_18"] == 1 or \
               attributes["search"]["include_over_18"] == "on":
                MODE["nsfw"] = True
            else:
                MODE["nsfw"] = False

    else:
        if "queries" in attributes:
            if not ("submitted" in attributes or \
                    "posts" in attributes):

                if "t" in attributes["queries"]:
                    MODE["time"] = attributes["queries"]["t"]
                else:
                    MODE["time"] = "day"
            else:
                if "t" in attributes["queries"]:
                    MODE["time"] = attributes["queries"]["t"]
                else:
                    MODE["time"] = "all"

                if "sort" in attributes["queries"]:
                    MODE["sort"] = attributes["queries"]["sort"]
                else:
                    MODE["sort"] = "new"
        else:
            MODE["time"] = "day"
               
    if "subreddit" in attributes and not "search" in attributes:
        MODE["subreddit"] = attributes["subreddit"]

    elif "user" in attributes and not "search" in attributes:
        MODE["user"] = attributes["user"]

        if "submitted" in attributes:
            MODE["submitted"] = True
            if "sort" in attributes["submitted"]:
                MODE["sort"] = attributes["submitted"]["sort"]
            elif "sort" in MODE:
                pass
            else:
                MODE["sort"] = "new"

            if "t" in attributes["submitted"]:
                MODE["time"] = attributes["submitted"]["t"]
            else:
                MODE["time"] = "all"

        elif "saved" in attributes:
            MODE["saved"] = True

        elif "upvoted" in attributes:
            MODE["upvoted"] = True
        
        elif "multireddit" in attributes:
            MODE["multireddit"] = attributes["multireddit"]

    if "sort" in attributes:
        MODE["sort"] = attributes["sort"]
    elif "sort" in MODE:
        pass
    else:
        MODE["sort"] = "hot"
 
    return MODE

if __name__ == "__main__":
    while True:
        link = input("> ")
        pprint(LinkDesigner(link))