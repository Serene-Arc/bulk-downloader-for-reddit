# Bulk Downloader for Reddit

Downloads media from reddit posts. Made by [u/aliparlakci](https://reddit.com/u/aliparlakci)

## What it can do

- Can get posts from: frontpage, subreddits, multireddits, redditor's submissions, upvoted and saved posts; search results or just plain reddit links
- Sorts posts by hot, top, new and so on
- Downloads **REDDIT** images and videos, **IMGUR** images and albums, **GFYCAT** links, **EROME** images and albums, **SELF POSTS** and any link to a **DIRECT IMAGE**
- Skips the existing ones
- Puts post title and OP's name in file's name
- Puts every post to its subreddit's folder
- Saves a reusable copy of posts' details that are found so that they can be re-downloaded again
- Logs failed ones in a file to so that you can try to download them later

## Installation

You can use it either as a Python script or `bulk-downloader-for-reddit.exe` file.

### Python script

* Download this repository ([latest zip](https://github.com/aliparlakci/bulk-downloader-for-reddit/archive/master.zip) or `git clone git@github.com:aliparlakci/bulk-downloader-for-reddit.git`).
* Enter its folder.
* Run `python ./script.py` from the command-line (MacOSX or Linux command line; it may work with Anaconda prompt).

It uses Python 3.6 and above. It won't work with Python 3.5 or any Python 2.x. If you have a trouble setting it up, see [here](docs/COMPILE_FROM_SOURCE.md).


### Executable

For Windows, [download the latest release](https://github.com/aliparlakci/bulk-downloader-for-reddit/releases/latest).


### Setting up the script

You need to create an imgur developer app in order API to work. Go to https://api.imgur.com/oauth2/addclient and fill the form (It does not really matter how you fill it).

It should redirect you to a page where it shows your **imgur_client_id** and **imgur_client_secret**.

When you run it for the first time, it will automatically create `config.json` file containing `imgur_client_id`, `imgur_client_secret`, `reddit_username` and `reddit_refresh_token`.


## Running

You can run it it an interactive mode, or using [command-line arguments](docs/COMMAND_LINE_ARGUMENTS.md) (also aviable via `python ./script.py --help` or `bulk-downloader-for-reddit.exe --help`).

To run the interactive mode, simply use `python ./script.py` or `bulk-downloader-for-reddit.exe` without any commands

### Example for an interactive script

```
(py37) bulk-downloader-for-reddit user$ python ./script.py

Bulk Downloader for Reddit v1.6.5
Written by Ali PARLAKCI – parlakciali@gmail.com

https://github.com/aliparlakci/bulk-downloader-for-reddit/

download directory: downloads/dataisbeautiful_last_few
select program mode:

    [1] search
    [2] subreddit
    [3] multireddit
    [4] submitted
    [5] upvoted
    [6] saved
    [7] log
    [0] exit

> 2
(type frontpage for all subscribed subreddits,
 use plus to seperate multi subreddits: pics+funny+me_irl etc.)

subreddit: dataisbeautiful

select sort type:

    [1] hot
    [2] top
    [3] new
    [4] rising
    [5] controversial
    [0] exit

> 1

limit (0 for none): 50

GETTING POSTS


(1/24) – r/dataisbeautiful
AutoModerator_[Battle]_DataViz_Battle_for_the_month_of_April_2019__Visualize_the_April_Fool's_Prank_for_2019-04-01_on__r_DataIsBeautiful_b8ws37.md
Downloaded

(2/24) – r/dataisbeautiful
AutoModerator_[Topic][Open]_Open_Discussion_Monday_—_Anybody_can_post_a_general_visualization_question_or_start_a_fresh_discussion!_bg1wej.md
Downloaded

...

Total of 24 links downloaded!

Press enter to quit
```


## FAQ

### How can I change my credentials?
- All of the user data is held in **config.json** file which is in a folder named "Bulk Downloader for Reddit" in your **Home** directory. You can edit
  them, there.

### What do the dots resemble when getting posts?
- Each dot means that 100 posts are scanned.

### Getting posts takes too long.
- You can press *Ctrl+C* to interrupt it and start downloading.

### How are the filenames formatted?
- **Self posts** and **images** that do not belong to an album and **album folders** are formatted as:  
  `[SUBMITTER NAME]_[POST TITLE]_[REDDIT ID]`  
  You can use *reddit id* to go to post's reddit page by going to link reddit.com/[REDDIT ID]

- An **image in an album** is formatted as:  
  `[ITEM NUMBER]_[IMAGE TITLE]_[IMGUR ID]`  
  Similarly, you can use *imgur id* to go to image's imgur page by going to link imgur.com/[IMGUR ID].

### How do I open self post files?
- Self posts are held at reddit as styled with markdown. So, the script downloads them as they are in order not to lose their stylings.
  However, there is a [great Chrome extension](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk) for viewing Markdown files with its styling. Install it and open the files with [Chrome](https://www.google.com/intl/tr/chrome/).  

  However, they are basically text files. You can also view them with any text editor such as Notepad on Windows, gedit on Linux or Text Editor on MacOS

## Changelog

* [See the changes on *master* here](docs/CHANGELOG.md)
