# Architecture

  1. Arguments are passed to an instance of RedditDownloader
  2. Internal objects are created
     
      - Formatter created
      - Filter created
      - Configuration loaded
      - Reddit instance created
     
  3. Reddit lists scraped
  
To actually download, the following happens:
  
  1. RedditDownloader uses DownloadFactory to find the right module for a submission
  2. Downloader instance created
  3. Downloader returns a list of Resource objects (lists may have one objects)
  4. RedditDownloader checks if it already exists
  5. RedditDownloader checks against the DownloadFilter created earlier
  6. RedditDownloader creates a formatted file path base on the Resource with FileNameFormatter
  7. Resource content is written to disk
  