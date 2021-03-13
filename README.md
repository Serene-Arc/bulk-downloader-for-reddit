# Bulk Downloader for Reddit

This is a tool to download data from Reddit.

## Usage

The BDFR works by taking submissions from a variety of "sources" from Reddit and then parsing them to download. These sources might be a subreddit, multireddit, a user list, or individual links. These sources are combined and downloaded to disk, according to a naming and organisational scheme defined by the user.

Many websites and links are supported:

  - Direct Links (links leading to a file)
  - Erome
  - Gfycat
  - Gif Delivery Network
  - Imgur
  - Reddit Galleries
  - Reddit Text Posts
  - Reddit Videos
  - Redgifs
  - Youtube

## Options

The following options are common between both the `archive` and `download` commands of the BDFR.

- `directory`
  - This is the directory to which the BDFR will download and place all files
- `--authenticate`
  - This flag will make the BDFR attempt to use an authenticated Reddit session
  - See[Authentication](#authentication) for more details
- `--config`
  - If the path to a configuration file is supplied with this option, the BDFR will use the specified config
  - See[Configuration Files](#configuration-files) for more details
- `--saved`
  - This option will make the BDFR use the supplied user's saved posts list as a download source
  - This requires an authenticated Reddit instance, using the `--authenticate` flag, as well as `--user` set to `me`
- `--search`
  - This will apply the specified search term to specific lists when scraping submissions
  - A search term can only be applied to subreddits and multireddits, supplied with the `- s` and `-m` flags respectively
- `--submitted`
  - This will use a user's submissions as a source
  - A user must be specified with `--user`
- `--upvoted`
  - This will use a user's upvoted posts as a source of posts to scrape
  - This requires an authenticated Reddit instance, using the `--authenticate` flag, as well as `--user` set to `me`
- `-L, --limit`
  - This is the limit on the number of submissions retrieve
  - Note that this limit applies to **each source individually** e.g. if a `--limit` of 10 and three subreddits are provided, then 30 total submissions will be scraped
  - If it is not supplied, then the BDFR will default to the maximum allowed by Reddit, roughly 1000 posts. **We cannot bypass this.**
- `-S, --sort`
  - This is the sort type for each applicable submission source supplied to the BDFR
  - This option does not apply to upvoted or saved posts when scraping from these sources
  - The following options are available:
    - `controversial`
    - `hot`
    - `new`
    - `relevance` (only available when using `--search`)
    - `rising`
    - `top`
- `-l, --link`
  - This is a direct link to a submission to download, either as a URL or an ID
  - Can be specified multiple times
- `-m, --multireddit`
  - This is the name of a multireddit to add as a source
  - Can be specified multiple times
  - The specified multireddits must all belong to the user specified with the `--user` option
- `-s, --subreddit`
  - This adds a subreddit as a source
  - Can be used mutliple times
- `-t, --time`
  - This is the time filter that will be applied to all applicable sources
  - This option does not apply to upvoted or saved posts when scraping from these sources
  - The following options are available:
    - `all`
    - `hour`
    - `day`
    - `week`
    - `month`
    - `year`
- `-u, --user`
  - This specifies the user to scrape in concert with other options
  - When using `--authenticate`, `--user me` can be used to refer to the authenticated user
- `-v, --verbose`
  - Increases the verbosity of the program
  - Can be specified multiple times

### Downloader Options

The following options apply only to the `download` command. This command downloads the files and resources linked to in the submission, or a text submission itself, to the disk in the specified directory.

- `--no-dupes`
  - This flag will not redownload files if they already exist somewhere in the root folder
  - This is calculated by MD5 hash
- `--search-existing`
  - This will make the BDFR compile the hashes for every file in `directory` and store them to remove duplicates if `--no-dupes` is also supplied
- `--set-file-scheme`
  - Sets the scheme for files
  - See[Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--set-folder-scheme`
  - Sets the scheme for folders
  - See[Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--skip-domain`
  - This adds domains to the download filter i.e. submissions coming from these domains will not be downloaded
  - Can be specified multiple times
- `--skip`
  - This adds file types to the download filter i.e. submissions with one of the supplied file extensions will not be downloaded
  - Can be specified multiple times

## Authentication

The BDFR uses OAuth2 authentication to connect to Reddit if authentication is required. This means that it is a secure, token - based system for making requests. This also means that the BDFR only has access to specific parts of the account authenticated, by default only saved posts, upvoted posts, and the identity of the authenticated account. Note that authentication is not required unless accessing private things like upvoted posts, saved posts, and private multireddits.

To authenticate, the BDFR will first look for a token in the configuration file that signals that there's been a previous authentication. If this is not there, then the BDFR will attempt to register itself with your account. This is normal, and if you run the program, it will pause and show a Reddit URL. Click on this URL and it will take you to Reddit, where the permissions being requested will be shown. Confirm it, and the BDFR will save a token that will allow it to authenticate with Reddit from then on.

## Changing Permissions

Most users will not need to do anything extra to use any of the current features. However, if additional features such as scraping messages, PMs, etc are added in the future, these will require additional scopes. Additionally, advanced users may wish to use the BDFR with their own API key and secret. There is normally no need to do this, but it is allowed by the BDFR.

The configuration file for the BDFR contains the API secret and key, as well as the scopes that the BDFR will request when registering itself to a Reddit account via OAuth2. These can all be changed if the user wishes, however do not do so if you don't know what you are doing. The defaults are specifically chosen to have a very low security risk if your token were to be compromised, however unlikely that actually is . Never grant more permissions than you absolutely need.

For more details on the configuration file and the values therein, see[Configuration Files](#configuration-files).

## Folder and File Name Schemes

## Configuration Files
