# Bulk Downloader for Reddit
This program downloads imgur, gfycat and direct image and video links of saved posts from a reddit account. It is written in Python 3.
  
**PLEASE** post any issue you have with the script to [Issues](https://github.com/aliparlakci/bulk-downloader-for-reddit/issues) tab. Since I don't have any testers or contributers I need your feedback.

## What it can do
- Can get posts from: frontpage, subreddits, multireddits, redditor's submissions, upvoted and saved posts; search results or just plain reddit links
- Sorts posts by hot, top, new and so on
- Downloads imgur albums, gfycat links, [self posts](#i-can-t-open-the-self-post-files-) and any link to a direct image
- Skips the existing ones
- Puts post titles to file's name
- Puts every post to its subreddit's folder
- Saves a reusable copy of posts' details that are found so that they can be re-downloaded again
- Logs failed ones in a file to so that you can try to download them later
- Can run with double-clicking on Windows

## [Download the latest release](https://github.com/aliparlakci/bulk-downloader-for-reddit/releases/latest)

## How it works
  
For **Windows** users, there is an executable file to run easily without installing a third party program. But if you are a paranoid like me, you can **[compile it from source code](docs/COMPILE_FROM_SOURCE.md)**.
  
**Linux** and **MacOS** users have to **[compile it from source code](docs/COMPILE_FROM_SOURCE.md)**.

Script also accepts **command-line arguments**, get further information from **[`python script.py --help`](docs/COMMAND_LINE_ARGUMENTS.md)**

## Setting up the script
Because this is not a commercial app, you need to create an imgur developer app in order API to work.

### Creating an imgur app
* Go to https://api.imgur.com/oauth2/addclient
* Enter a name into the **Application Name** field.
* Pick **Anonymous usage without user authorization** as an **Authorization type**\*
* Enter your email into the Email field.
* Correct CHAPTCHA
* Click **submit** button  
  
It should redirect to a page which shows your **imgur_client_id** and **imgur_client_secret**
  
\* Select **OAuth 2 authorization without a callback URL** first then select **Anonymous usage without user authorization** if it says *Authorization callback URL: required*

## FAQ
### I can't open the self post files.
- Self posts are held at reddit as styled with markdown. So, the script downloads them as they are in order not to lose their stylings.
  However, there is a [great Chrome extension](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk) for viewing Markdown files with its styling. Install it and open the files with [Chrome](https://www.google.com/intl/tr/chrome/).

## Changelog
### [11/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/a28a7776ab826dea2a8d93873a94cd46db3a339b)
- Improvements on UX and UI
- Added logging errors to CONSOLE_LOG.txt
- Using current directory if directory has not been given yet.

### [10/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/ffe3839aee6dc1a552d95154d817aefc2b66af81)
- Added support for *self* post
- Now getting posts is quicker
