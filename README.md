# Bulk Downloader for Reddit
Downloads media from reddit posts.

## [Download the latest release](https://github.com/aliparlakci/bulk-downloader-for-reddit/releases/latest)

## What it can do
- Can get posts from: frontpage, subreddits, multireddits, redditor's submissions, upvoted and saved posts; search results or just plain reddit links
- Sorts posts by hot, top, new and so on
- Downloads **REDDIT** images and videos, **IMGUR** images and albums, **GFYCAT** links, **EROME** images and albums, **SELF POSTS** and any link to a **DIRECT IMAGE**
- Skips the existing ones
- Puts post title and OP's name in file's name
- Puts every post to its subreddit's folder
- Saves a reusable copy of posts' details that are found so that they can be re-downloaded again
- Logs failed ones in a file to so that you can try to download them later

## **[Compiling it from source code](docs/COMPILE_FROM_SOURCE.md)**
*\* MacOS users have to use this option.*

## Additional options
Script also accepts additional options via command-line arguments. Get further information from **[`--help`](docs/COMMAND_LINE_ARGUMENTS.md)**

## Setting up the script
You need to create an imgur developer app in order API to work. Go to https://api.imgur.com/oauth2/addclient and fill the form (It does not really matter how you fill it).
  
It should redirect you to a page where it shows your **imgur_client_id** and **imgur_client_secret**.
  
## [FAQ](docs/FAQ.md)

## [Changes on *master*](docs/CHANGELOG.md)