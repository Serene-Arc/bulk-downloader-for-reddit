# Bulk Downloader for Reddit

This is a tool to download submissions or submission data from Reddit. It can be used to archive data or even crawl Reddit to gather research data. The BDFR is flexible and can be used in scripts if needed through an extensive command-line interface.

## Usage

The BDFR works by taking submissions from a variety of "sources" from Reddit and then parsing them to download. These sources might be a subreddit, multireddit, a user list, or individual links. These sources are combined and downloaded to disk, according to a naming and organisational scheme defined by the user.

There are two modes to the BDFR: download, and archive. Each one has a command that performs similar but distinct functions. The `download` command will download the resource linked in the Reddit submission, such as the images, video, etc linked. The `archive` command will download the submission data itself and store it, such as the submission details, upvotes, text, statistics, as well as all the comments on that submission. These can then be saved in a data markup language form, such as JSON, XML, or YAML.

Many websites and links are supported for the downloader:

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

### Options

The following options are common between both the `archive` and `download` commands of the BDFR.

- `directory`
  - This is the directory to which the BDFR will download and place all files
- `--authenticate`
  - This flag will make the BDFR attempt to use an authenticated Reddit session
  - See[Authentication](#authentication) for more details
- `--config`
  - If the path to a configuration file is supplied with this option, the BDFR will use the specified config
  - See[Configuration Files](#configuration) for more details
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
  - Default is max possible
  - Note that this limit applies to **each source individually** e.g. if a `--limit` of 10 and three subreddits are provided, then 30 total submissions will be scraped
  - If it is not supplied, then the BDFR will default to the maximum allowed by Reddit, roughly 1000 posts. **We cannot bypass this.**
- `-S, --sort`
  - This is the sort type for each applicable submission source supplied to the BDFR
  - This option does not apply to upvoted or saved posts when scraping from these sources
  - The following options are available:
    - `controversial`
    - `hot` (default)
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
    - `all` (default)
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

#### Downloader Options

The following options apply only to the `download` command. This command downloads the files and resources linked to in the submission, or a text submission itself, to the disk in the specified directory.

- `--no-dupes`
  - This flag will not redownload files if they already exist somewhere in the root folder tree
  - This is calculated by MD5 hash
- `--search-existing`
  - This will make the BDFR compile the hashes for every file in `directory` and store them to remove duplicates if `--no-dupes` is also supplied
- `--set-file-scheme`
  - Sets the scheme for files
  - Default is `{REDDITOR}_{TITLE}_{POSTID}`
  - See[Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--set-folder-scheme`
  - Sets the scheme for folders
  - Default is `{SUBREDDIT}`
  - See[Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--skip-domain`
  - This adds domains to the download filter i.e. submissions coming from these domains will not be downloaded
  - Can be specified multiple times
- `--skip`
  - This adds file types to the download filter i.e. submissions with one of the supplied file extensions will not be downloaded
  - Can be specified multiple times

#### Archiver Options

The following options are for the `archive` command specifically.

- `-f, --format`
  - This specifies the format of the data file saved to disk
  - The following formats are available:
    - `json` (default)
    - `xml`
    - `yaml`

## Authentication

The BDFR uses OAuth2 authentication to connect to Reddit if authentication is required. This means that it is a secure, token - based system for making requests. This also means that the BDFR only has access to specific parts of the account authenticated, by default only saved posts, upvoted posts, and the identity of the authenticated account. Note that authentication is not required unless accessing private things like upvoted posts, saved posts, and private multireddits.

To authenticate, the BDFR will first look for a token in the configuration file that signals that there's been a previous authentication. If this is not there, then the BDFR will attempt to register itself with your account. This is normal, and if you run the program, it will pause and show a Reddit URL. Click on this URL and it will take you to Reddit, where the permissions being requested will be shown. Confirm it, and the BDFR will save a token that will allow it to authenticate with Reddit from then on.

## Changing Permissions

Most users will not need to do anything extra to use any of the current features. However, if additional features such as scraping messages, PMs, etc are added in the future, these will require additional scopes. Additionally, advanced users may wish to use the BDFR with their own API key and secret. There is normally no need to do this, but it is allowed by the BDFR.

The configuration file for the BDFR contains the API secret and key, as well as the scopes that the BDFR will request when registering itself to a Reddit account via OAuth2. These can all be changed if the user wishes, however do not do so if you don't know what you are doing. The defaults are specifically chosen to have a very low security risk if your token were to be compromised, however unlikely that actually is . Never grant more permissions than you absolutely need.

For more details on the configuration file and the values therein, see[Configuration Files](#configuration).

## Folder and File Name Schemes

The naming and folder schemes for the BDFR are both completely customisable. A number of different fields can be given which will be replaced with properties from a submission when downloading it. The scheme format takes the form of `{KEY}`, where `KEY` is a string from the below list.

  - `DATE`
  - `FLAIR`
  - `POSTID`
  - `REDDITOR`
  - `SUBREDDIT`
  - `TITLE`
  - `UPVOTES`

Each of these can be enclosed in curly bracket, `{}`, and included in the name. For example, to just title every downloaded post with the unique submission ID, you can use `{POSTID}`. Statis strings can also be included, such as `download_{POSTID}` which will not change from submission to submission.

At least one key *must* be included in the file scheme, otherwise an error will be thrown. The folder scheme however, can be null or a simple static string. In the former case, all files will be placed in the folder specified with the `directory` argument. If the folder scheme is a static string, then all submissions will be placed in a folder of that name.

## Configuration

The configuration files are, by default, stored in the configuration directory for the user. This differs depending on the OS that the BDFR is being run on. For Windows, this will be `C:\Documents and Settings\<User>\Application Data\Local Settings\BDFR\bulkredditdownloader` or `C:\Documents and Settings\<User>\Application Data\BDFR\bulkredditdownloader`. On Mac OSX, this will be `~/Library/Application Support/bulkredditdownloader`. Lastly, on a Linux system, this will be `~/.local/share/bulkredditdownloader`.

The logging output for each run of the BDFR will be saved to this directory in the file `log_output.txt`. If you need to submit a bug, it is this file that you will need to submit with the report.

### Configuration File

The `config.cfg` is the file that supplies the BDFR with the configuration to use. At the moment, the following keys ** must ** be included in the configuration file supplied.

  - `client_id`
  - `client_secret`
  - `scopes`

All of these should not be modified unless you know what you're doing, as the default values will enable the BDFR to function just fine. A configuration is included in the BDFR when it is installed, and this will be placed in the configuration directory as the default.

## Contributing

If you wish to contribute, see [Contributing](docs/CONTRIBUTING.md) for more information.

When reporting any issues or interacting with the developers, please follow the [Code of Conduct](docs/CODE_OF_CONDUCT.md).
