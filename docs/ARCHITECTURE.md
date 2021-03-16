# Architecture

When the project was rewritten for v2, the goal was to make the codebase easily extensible and much easier to read and modify. However, this document provides a step-by-step look through the process that the BDFR goes through, so that any prospective developers can more easily grasp the way the code works.

## The Download Process

The BDFR is organised around a central object, the RedditDownloader class. The Archiver object extends and inherits from this class.

  1. The RedditDownloader parses all the arguments and configuration options, held in the Configuration object, and creates a variety of internal objects for use, such as the file name formatter, download filter, etc. 
  
  2. The RedditDownloader scrapes raw submissions from Reddit via several methods relating to different sources. A source is defined as a single stream of submissions from a subreddit, multireddit, or user list.

  3. These raw submissions are passed to the DownloaderFactory class to select the specialised downloader class to use. Each of these are for a specific website or link type, with some catch-all classes like Direct. 

  4. The BaseDownloader child, spawned by DownloaderFactory, takes the link and does any necessary processing to find the direct link to the actual resource. 

  5. This is returned to the RedditDownloader in the form of a Resource object. This holds the URL and some other information for the final resource.

  6. The Resource is passed through the DownloadFilter instantiated in step 1.
  
  7. The destination file name for the Resource is calculated. If it already exists, then the Resource will be discarded.

  8. Here the actual data is downloaded to the Resource and a hash calculated which is used to find duplicates.

  9. Only then is the Resource written to the disk.

This is the step-by-step process that the BDFR goes through to download a Reddit post.

## Adding another Supported Site

This is one of the easiest changes to do with the code. First, any new class must inherit from the BaseDownloader class which provided an abstract parent to implement. However, take note of the other classes as well. Many downloaders can inherit from one another instead of just the BaseDownloader. For example, the VReddit class, used for downloading video from Reddit, inherits almost all of its code from the YouTube class. **Minimise code duplication wherever possible**.

Once the downloader class has been written **and tests added** for it as well, then the regex string for the site's URLs can be added to the DownloaderFactory. Then additional tests must be added for the DownloadFactory to ensure that the appropriate classes are called when the right URLs are passed to the factory.

## Adding Other Features


