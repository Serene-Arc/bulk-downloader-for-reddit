# Bulk Downloader for Reddit
Downloads media from reddit posts.

## [Download the latest release here](https://github.com/aliparlakci/bulk-downloader-for-reddit/releases/latest)

## What it can do
- Can get posts from: frontpage, subreddits, multireddits, redditor's submissions, upvoted and saved posts; search results or just plain reddit links
- Sorts posts by hot, top, new and so on
- Downloads **REDDIT** images and videos, **IMGUR** images and albums, **GFYCAT** links, **EROME** images and albums, **SELF POSTS** and any link to a **DIRECT IMAGE**
- Skips the existing ones
- Puts post title and OP's name in file's name
- Puts every post to its subreddit's folder
- Saves a reusable copy of posts' details that are found so that they can be re-downloaded again
- Logs failed ones in a file to so that you can try to download them later

## **Compiling it from source code**
MacOS users have to use this option. See *[here](docs/COMPILE_FROM_SOURCE.md)*

## Additional options
Script also accepts additional options via command-line arguments. Get further information from **[`--help`](docs/COMMAND_LINE_ARGUMENTS.md)**

## Setting up the script
You need to create an imgur developer app in order API to work. Go to https://api.imgur.com/oauth2/addclient and fill the form (It does not really matter how you fill it).
  
It should redirect you to a page where it shows your **imgur_client_id** and **imgur_client_secret**.
  
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

## [See the changes on *master* here](docs/CHANGELOG.md)