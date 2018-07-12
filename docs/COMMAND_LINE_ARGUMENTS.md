# Using command-line arguments

See **[compiling from source](COMPILE_FROM_SOURCE.md)** page first unless you are using the .exe file. If you are using the .exe file, see [using terminal](COMPILE_FROM_SOURCE.md#using-terminal) and come back.

***Use*** `.\script.exe` ***if you are using the executable***.
```console
$ python script.py --help
usage: script.py [-h] [--directory DIRECTORY] [--link link] [--saved]
                 [--submitted] [--upvoted] [--log LOG FILE]
                 [--subreddit SUBREDDIT [SUBREDDIT ...]]
                 [--multireddit MULTIREDDIT] [--user redditor]
                 [--search query] [--sort SORT TYPE] [--limit Limit]
                 [--time TIME_LIMIT] [--NoDownload]

This program downloads media from reddit posts

optional arguments:
  -h, --help            show this help message and exit
  --directory DIRECTORY
                        Specifies the directory where posts will be downloaded
                        to
  --link link, -l link  Get posts from link
  --saved               Triggers saved mode
  --submitted           Gets posts of --user
  --upvoted             Gets upvoted posts of --user
  --log LOG FILE        Triggers log read mode and takes a log file
  --subreddit SUBREDDIT [SUBREDDIT ...]
                        Triggers subreddit mode and takes subreddit's name
                        without r/. use "frontpage" for frontpage
  --multireddit MULTIREDDIT
                        Triggers multireddit mode and takes multireddit's name
                        without m/
  --user redditor       reddit username if needed. use "me" for current user
  --search query        Searches for given query in given subreddits
  --sort SORT TYPE      Either hot, top, new, controversial, rising or
                        relevance default: hot
  --limit Limit         default: unlimited
  --time TIME_LIMIT     Either hour, day, week, month, year or all. default:
                        all
  --NoDownload          Just gets the posts and store them in a file for
                        downloading later
```

# Examples

- **Use `python3` instead of `python` if you are using *MacOS* or *Linux***  

```console
python script.py
```

```console
.\script.exe .\\NEW_FOLDER --search cats --sort new --time all --subreddit gifs pics --NoDownload
```

```console
python script.py --directory .\\NEW_FOLDER --sort new --time all --limit 10 --link "https://www.reddit.com/r/gifs/search?q=dogs&restrict_sr=on&type=link&sort=new&t=month"
```

```console
python script.py --directory .\\NEW_FOLDER --link "https://www.reddit.com/r/learnprogramming/comments/7mjw12/"
```

```console
python script.py --directory .\\NEW_FOLDER --search cats --sort new --time all --subreddit gifs pics --NoDownload
```

```console
python script.py --directory .\\NEW_FOLDER --user [USER_NAME] --submitted --limit 10
```

```console
python script.py --directory .\\NEW_FOLDER --multireddit good_subs --user [USER_NAME] --sort top --time week --limit 250
```

```console
python script.py --directory .\\NEW_FOLDER\\ANOTHER_FOLDER --saved --limit 1000
```

```console
python script.py --directory C:\\NEW_FOLDER\\ANOTHER_FOLDER --log UNNAMED_FOLDER\\FAILED.json
```

# FAQ
## I can't startup the script no matter what.
See **[finding the correct prefix for Python](COMPILE_FROM_SOURCE.md#finding-the-correct-prefix-for-python)**
