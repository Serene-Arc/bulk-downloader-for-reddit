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

## How it works
- For **Windows** and **Linux** users, there are executable files to run easily without installing a third party program. But if you are a paranoid like me, you can **[compile it from source code](docs/COMPILE_FROM_SOURCE.md)**.
  
- **MacOS** users have to **[compile it from source code](docs/COMPILE_FROM_SOURCE.md)**.

## Additional options
Script also accepts additional options via command-line arguments. Get further information from **[`--help`](docs/COMMAND_LINE_ARGUMENTS.md)**

## Setting up the script
  You need to create an imgur developer app in order API to work. Go to https://api.imgur.com/oauth2/addclient and fill the form (It does not really matter how you fill it). It should redirect you to a page where it shows your **imgur_client_id** and **imgur_client_secret**.
  
## FAQ
### What do the dots resemble when getting posts?
- Each dot means that 100 posts are scanned. 
  
### Getting posts is taking too long.
- You can press Ctrl+C to interrupt it and start downloading.
  
### How are filenames formatted?
- Self posts and images that are not belong to an album are formatted as **`[SUBMITTER NAME]_[POST TITLE]_[REDDIT ID]`**.
  You can use *reddit id* to go to post's reddit page by going to link **reddit.com/[REDDIT ID]**
  
- An image in an imgur album is formatted as **`[ITEM NUMBER]_[IMAGE TITLE]_[IMGUR ID]`**
  Similarly, you can use *imgur id* to go to image's imgur page by going to link **imgur.com/[IMGUR ID]**.

### How do I open self post files?
- Self posts are held at reddit as styled with markdown. So, the script downloads them as they are in order not to lose their stylings.
  However, there is a [great Chrome extension](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk) for viewing Markdown files with its styling. Install it and open the files with [Chrome](https://www.google.com/intl/tr/chrome/).  

  However, they are basically text files. You can also view them with any text editor such as Notepad on Windows, gedit on Linux or Text Editor on MacOS

### How can I change my credentials?
- All of the user data is held in **config.json** file which is in a folder named "Bulk Downloader for Reddit" in your **Home** directory. You can edit 
  them, there.

## Changes on *master*
### [06/08/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/210238d0865febcb57fbd9f0b0a7d3da9dbff384)
- Sending headers when requesting a file in order not to be rejected by server

### [04/08/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/426089d0f35212148caff0082708a87017757bde)
- Disabled printing post types to console

### [30/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/af294929510f884d92b25eaa855c29fc4fb6dcaa)
- Now opens web browser and goes to Imgur when prompts for Imgur credentials

### [26/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/1623722138bad80ae39ffcd5fb38baf80680deac)
- Improved verbose mode
- Minimalized the console output
- Added quit option for auto quitting the program after process finishes

### [25/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/1623722138bad80ae39ffcd5fb38baf80680deac)
- Added verbose mode
- Stylized the console output

### [24/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/7a68ff3efac9939f9574c2cef6184b92edb135f4)
- Added OP's name to file names (backwards compatible)
- Deleted # char from file names (backwards compatible)
- Improved exception handling

### [23/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/7314e17125aa78fd4e6b28e26fda7ec7db7e0147)
- Splited download() function
- Added erome support
- Removed exclude feature
- Bug fixes

### [22/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/6e7463005051026ad64006a8580b0b5dc9536b8c)
- Put log files in a folder named "LOG_FILES"
- Fixed the bug that makes multireddit mode unusable

### [21/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/4a8c2377f9fb4d60ed7eeb8d50aaf9a26492462a)
- Added exclude mode

### [20/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/7548a010198fb693841ca03654d2c9bdf5742139)
- "0" input for no limit
- Fixed the bug that recognizes none image direct links as image links

### [19/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/41cbb58db34f500a8a5ecc3ac4375bf6c3b275bb)
- Added v.redd.it support
- Added custom exception descriptions to FAILED.json file
- Fixed the bug that prevents downloading some gfycat URLs

### [13/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/9f831e1b784a770c82252e909462871401a05c11)
- Changed config.json file's path to home directory

### [12/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/50a77f6ba54c24f5647d5ea4e177400b71ff04a7)
- Added binaries for Windows and Linux
- Wait on KeyboardInterrupt
- Accept multiple subreddit input
- Fixed the bug that prevents choosing "[0] exit" with typing "exit"

### [11/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/a28a7776ab826dea2a8d93873a94cd46db3a339b)
- Improvements on UX and UI
- Added logging errors to CONSOLE_LOG.txt
- Using current directory if directory has not been given yet.

### [10/07/2018](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/ffe3839aee6dc1a552d95154d817aefc2b66af81)
- Added support for *self* post
- Now getting posts is quicker
