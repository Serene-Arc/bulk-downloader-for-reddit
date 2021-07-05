# Bulk Downloader for Reddit
[![PyPI version](https://img.shields.io/pypi/v/bdfr.svg)](https://pypi.python.org/pypi/bdfr)
[![PyPI downloads](https://img.shields.io/pypi/dm/bdfr)](https://pypi.python.org/pypi/bdfr)
[![Python Test](https://github.com/aliparlakci/bulk-downloader-for-reddit/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/aliparlakci/bulk-downloader-for-reddit/actions/workflows/test.yml)

This is a tool to download submissions or submission data from Reddit. It can be used to archive data or even crawl Reddit to gather research data. The BDFR is flexible and can be used in scripts if needed through an extensive command-line interface. [List of currently supported sources](#list-of-currently-supported-sources)

If you wish to open an issue, please read [the guide on opening issues](docs/CONTRIBUTING.md#opening-an-issue) to ensure that your issue is clear and contains everything it needs to for the developers to investigate.

## Installation
*Bulk Downloader for Reddit* needs Python version 3.9 or above. Please update Python before installation to meet the requirement. Then, you can install it as such:
```bash
python3 -m pip install bdfr --upgrade
```
**To update BDFR**, run the above command again after the installation.

### AUR Package
If on Arch Linux or derivative operating systems such as Manjaro, the BDFR can be installed through the AUR.

- Latest Release: https://aur.archlinux.org/packages/python-bdfr/
- Latest Development Build: https://aur.archlinux.org/packages/python-bdfr-git/

### Source code
If you want to use the source code or make contributions, refer to [CONTRIBUTING](docs/CONTRIBUTING.md#preparing-the-environment-for-development)

## Usage

The BDFR works by taking submissions from a variety of "sources" from Reddit and then parsing them to download. These sources might be a subreddit, multireddit, a user list, or individual links. These sources are combined and downloaded to disk, according to a naming and organisational scheme defined by the user.

There are three modes to the BDFR: download, archive, and clone. Each one has a command that performs similar but distinct functions. The `download` command will download the resource linked in the Reddit submission, such as the images, video, etc. The `archive` command will download the submission data itself and store it, such as the submission details, upvotes, text, statistics, as and all the comments on that submission. These can then be saved in a data markup language form, such as JSON, XML, or YAML. Lastly, the `clone` command will perform both functions of the previous commands at once and is more efficient than running those commands sequentially.

Note that the `clone` command is not a true, failthful clone of Reddit. It simply retrieves much of the raw data that Reddit provides. To get a true clone of Reddit, another tool such as HTTrack should be used.

After installation, run the program from any directory as shown below:

```bash
python3 -m bdfr download
```

```bash
python3 -m bdfr archive
```

```bash
python3 -m bdfr clone
```

However, these commands are not enough. You should chain parameters in [Options](#options) according to your use case. Don't forget that some parameters can be provided multiple times. Some quick reference commands are:

```bash
python3 -m bdfr download ./path/to/output --subreddit Python -L 10
```
```bash
python3 -m bdfr download ./path/to/output --user me --saved --authenticate -L 25 --file-scheme '{POSTID}'
```
```bash
python3 -m bdfr download ./path/to/output --subreddit 'Python, all, mindustry' -L 10 --make-hard-links
```
```bash
python3 -m bdfr archive ./path/to/output --subreddit all --format yaml -L 500 --folder-scheme ''
```

## Options

The following options are common between both the `archive` and `download` commands of the BDFR.

- `directory`
  - This is the directory to which the BDFR will download and place all files
- `--authenticate`
  - This flag will make the BDFR attempt to use an authenticated Reddit session
  - See [Authentication](#authentication-and-security) for more details
- `--config`
  - If the path to a configuration file is supplied with this option, the BDFR will use the specified config
  - See [Configuration Files](#configuration) for more details
- `--disable-module`
  - Can be specified multiple times
  - Disables certain modules from being used
  - See [Disabling Modules](#disabling-modules) for more information and a list of module names
- `--include-id-file`
  - This will add any submission with the IDs in the files provided
  - Can be specified multiple times
  - Format is one ID per line
- `--log`
  - This allows one to specify the location of the logfile
  - This must be done when running multiple instances of the BDFR, see [Multiple Instances](#multiple-instances) below
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
      - This can be done by using `-m` multiple times
      - Multireddits can also be used to provide CSV multireddits e.g. `-m 'chess, favourites'`
  - The specified multireddits must all belong to the user specified with the `--user` option
- `-s, --subreddit`
  - This adds a subreddit as a source
  - Can be used mutliple times
    - This can be done by using `-s` multiple times
    - Subreddits can also be used to provide CSV subreddits e.g. `-m 'all, python, mindustry'`
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
  - `--time-format`
    - This specifies the format of the datetime string that replaces `{DATE}` in file and folder naming schemes
    - See [Time Formatting Customisation](#time-formatting-customisation) for more details, and the formatting scheme
- `-u, --user`
  - This specifies the user to scrape in concert with other options
  - When using `--authenticate`, `--user me` can be used to refer to the authenticated user
  - Can be specified multiple times for multiple users
    - If downloading a multireddit, only one user can be specified
- `-v, --verbose`
  - Increases the verbosity of the program
  - Can be specified multiple times

### Downloader Options

The following options apply only to the `download` command. This command downloads the files and resources linked to in the submission, or a text submission itself, to the disk in the specified directory.

- `--make-hard-links`
  - This flag will create hard links to an existing file when a duplicate is downloaded
  - This will make the file appear in multiple directories while only taking the space of a single instance
- `--max-wait-time`
  - This option specifies the maximum wait time for downloading a resource
  - The default is 120 seconds
  - See [Rate Limiting](#rate-limiting) for details
- `--no-dupes`
  - This flag will not redownload files if they already exist somewhere in the root folder tree
  - This is calculated by MD5 hash
- `--search-existing`
  - This will make the BDFR compile the hashes for every file in `directory` and store them to remove duplicates if `--no-dupes` is also supplied
- `--file-scheme`
  - Sets the scheme for files
  - Default is `{REDDITOR}_{TITLE}_{POSTID}`
  - See [Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--folder-scheme`
  - Sets the scheme for folders
  - Default is `{SUBREDDIT}`
  - See [Folder and File Name Schemes](#folder-and-file-name-schemes) for more details
- `--exclude-id`
  - This will skip the download of any submission with the ID provided
  - Can be specified multiple times
- `--exclude-id-file`
  - This will skip the download of any submission with any of the IDs in the files provided
  - Can be specified multiple times
  - Format is one ID per line
- `--skip-domain`
  - This adds domains to the download filter i.e. submissions coming from these domains will not be downloaded
  - Can be specified multiple times
- `--skip`
  - This adds file types to the download filter i.e. submissions with one of the supplied file extensions will not be downloaded
  - Can be specified multiple times
- `--skip-subreddit`
  - This skips all submissions from the specified subreddit
  - Can be specified multiple times
  - Also accepts CSV subreddit names

### Archiver Options

The following options are for the `archive` command specifically.

- `--all-comments`
  - When combined with the `--user` option, this will download all the user's comments
- `-f, --format`
  - This specifies the format of the data file saved to disk
  - The following formats are available:
    - `json` (default)
    - `xml`
    - `yaml`
- `--comment-context`
  - This option will, instead of downloading an individual comment, download the submission that comment is a part of
  - May result in a longer run time as it retrieves much more data

### Cloner Options

The `clone` command can take all the options listed above for both the `archive` and `download` commands since it performs the functions of both.

## Authentication and Security

The BDFR uses OAuth2 authentication to connect to Reddit if authentication is required. This means that it is a secure, token-based system for making requests. This also means that the BDFR only has access to specific parts of the account authenticated, by default only saved posts, upvoted posts, and the identity of the authenticated account. Note that authentication is not required unless accessing private things like upvoted posts, saved posts, and private multireddits.

To authenticate, the BDFR will first look for a token in the configuration file that signals that there's been a previous authentication. If this is not there, then the BDFR will attempt to register itself with your account. This is normal, and if you run the program, it will pause and show a Reddit URL. Click on this URL and it will take you to Reddit, where the permissions being requested will be shown. Read this and **confirm that there are no more permissions than needed to run the program**. You should not grant unneeded permissions; by default, the BDFR only requests permission to read your saved or upvoted submissions and identify as you.

If the permissions look safe, confirm it, and the BDFR will save a token that will allow it to authenticate with Reddit from then on.

## Changing Permissions

Most users will not need to do anything extra to use any of the current features. However, if additional features such as scraping messages, PMs, etc are added in the future, these will require additional scopes. Additionally, advanced users may wish to use the BDFR with their own API key and secret. There is normally no need to do this, but it *is* allowed by the BDFR.

The configuration file for the BDFR contains the API secret and key, as well as the scopes that the BDFR will request when registering itself to a Reddit account via OAuth2. These can all be changed if the user wishes, however do not do so if you don't know what you are doing. The defaults are specifically chosen to have a very low security risk if your token were to be compromised, however unlikely that actually is. Never grant more permissions than you absolutely need.

For more details on the configuration file and the values therein, see [Configuration Files](#configuration).

## Folder and File Name Schemes

The naming and folder schemes for the BDFR are both completely customisable. A number of different fields can be given which will be replaced with properties from a submission when downloading it. The scheme format takes the form of `{KEY}`, where `KEY` is a string from the below list.

  - `DATE`
  - `FLAIR`
  - `POSTID`
  - `REDDITOR`
  - `SUBREDDIT`
  - `TITLE`
  - `UPVOTES`

Each of these can be enclosed in curly bracket, `{}`, and included in the name. For example, to just title every downloaded post with the unique submission ID, you can use `{POSTID}`. Static strings can also be included, such as `download_{POSTID}` which will not change from submission to submission. For example, the previous string will result in the following submission file names:

  - `download_aaaaaa.png`
  - `download_bbbbbb.png`

At least one key *must* be included in the file scheme, otherwise an error will be thrown. The folder scheme however, can be null or a simple static string. In the former case, all files will be placed in the folder specified with the `directory` argument. If the folder scheme is a static string, then all submissions will be placed in a folder of that name. In both cases, there will be no separation between all submissions.

It is highly recommended that the file name scheme contain the parameter `{POSTID}` as this is **the only parameter guaranteed to be unique**. No combination of other keys will necessarily be unique and may result in posts being skipped as the BDFR will see files by the same name and skip the download, assuming that they are already downloaded.

## Configuration

The configuration files are, by default, stored in the configuration directory for the user. This differs depending on the OS that the BDFR is being run on. For Windows, this will be:

  - `C:\Users\<User>\AppData\Local\BDFR\bdfr`

If Python has been installed through the Windows Store, the folder will appear in a different place. Note that the hash included in the file path may change from installation to installation.

  - `C:\Users\<User>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\Local\BDFR\bdfr`

On Mac OSX, this will be:

  - `~/Library/Application Support/bdfr`. 
    
Lastly, on a Linux system, this will be:

  - `~/.config/bdfr/`

The logging output for each run of the BDFR will be saved to this directory in the file `log_output.txt`. If you need to submit a bug, it is this file that you will need to submit with the report.

### Configuration File

The `config.cfg` is the file that supplies the BDFR with the configuration to use. At the moment, the following keys **must** be included in the configuration file supplied.

  - `client_id`
  - `client_secret`
  - `scopes`

The following keys are optional, and defaults will be used if they cannot be found.

  - `backup_log_count`
  - `max_wait_time`
  - `time_format`
  - `disabled_modules`

All of these should not be modified unless you know what you're doing, as the default values will enable the BDFR to function just fine. A configuration is included in the BDFR when it is installed, and this will be placed in the configuration directory as the default.

Most of these values have to do with OAuth2 configuration and authorisation. The key `backup_log_count` however has to do with the log rollover. The logs in the configuration directory can be verbose and for long runs of the BDFR, can grow quite large. To combat this, the BDFR will overwrite previous logs. This value determines how many previous run logs will be kept. The default is 3, which means that the BDFR will keep at most three past logs plus the current one. Any runs past this will overwrite the oldest log file, called "rolling over". If you want more records of past runs, increase this number.

#### Time Formatting Customisation

The option `time_format` will specify the format of the timestamp that replaces `{DATE}` in filename and folder name schemes. By default, this is the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format which is highly recommended due to its standardised nature. If you don't **need** to change it, it is recommended that you do not. However, you can specify it to anything required with this option. The `--time-format` option supersedes any specification in the configuration file

The format can be specified through the [format codes](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior) that are standard in the Python `datetime` library.

#### Disabling Modules

The individual modules of the BDFR, used to download submissions from websites, can be disabled. This is helpful especially in the case of the fallback downloaders, since the `--skip-domain` option cannot be effectively used in these cases. For example, the Youtube-DL downloader can retrieve data from hundreds of websites and domains; thus the only way to fully disable it is via the `--disable-module` option.

Modules can be disabled through the command line interface for the BDFR or more permanently in the configuration file via the `disabled_modules` option. The list of downloaders that can be disabled are the following. Note that they are case-insensitive.

- `Direct`
- `Erome`
- `Gallery` (Reddit Image Galleries)
- `Gfycat`
- `Imgur`
- `Redgifs`
- `SelfPost` (Reddit Text Post)
- `Youtube`
- `YoutubeDlFallback`

### Rate Limiting

The option `max_wait_time` has to do with retrying downloads. There are certain HTTP errors that mean that no amount of requests will return the wanted data, but some errors are from rate-limiting. This is when a single client is making so many requests that the remote website cuts the client off to preserve the function of the site. This is a common situation when downloading many resources from the same site. It is polite and best practice to obey the website's wishes in these cases.

To this end, the BDFR will sleep for a time before retrying the download, giving the remote server time to "rest". This is done in 60 second increments. For example, if a rate-limiting-related error is given, the BDFR will sleep for 60 seconds before retrying. Then, if the same type of error occurs, it will sleep for another 120 seconds, then 180 seconds, and so on.

The option `--max-wait-time` and the configuration option `max_wait_time` both specify the maximum time the BDFR will wait. If both are present, the command-line option takes precedence. For instance, the default is 120, so the BDFR will wait for 60 seconds, then 120 seconds, and then move one. **Note that this results in a total time of 180 seconds trying the same download**. If you wish to try to bypass the rate-limiting system on the remote site, increasing the maximum wait time may help. However, note that the actual wait times increase exponentially if the resource is not downloaded i.e. specifying a max value of 300 (5 minutes), can make the BDFR pause for 15 minutes on one submission, not 5, in the worst case.

## Multiple Instances

The BDFR can be run in multiple instances with multiple configurations, either concurrently or consecutively. The use of scripting files facilitates this the easiest, either Powershell on Windows operating systems or Bash elsewhere. This allows multiple scenarios to be run with data being scraped from different sources, as any two sets of scenarios might be mutually exclusive i.e. it is not possible to download any combination of data from a single run of the BDFR. To download from multiple users for example, multiple runs of the BDFR are required.

Running these scenarios consecutively is done easily, like any single run. Configuration files that differ may be specified with the `--config` option to switch between tokens, for example. Otherwise, almost all configuration for data sources can be specified per-run through the command line.

Running scenarious concurrently (at the same time) however, is more complicated. The BDFR will look to a single, static place to put the detailed log files, in a directory with the configuration file specified above. If there are multiple instances, or processes, of the BDFR running at the same time, they will all be trying to write to a single file. On Linux and other UNIX based operating systems, this will succeed, though there is a substantial risk that the logfile will be useless due to garbled and jumbled data. On Windows however, attempting this will raise an error that crashes the program as Windows forbids multiple processes from accessing the same file.

The way to fix this is to use the `--log` option to manually specify where the logfile is to be stored. If the given location is unique to each instance of the BDFR, then it will run fine.

## List of currently supported sources

  - Direct links (links leading to a file)
  - Erome
  - Gfycat
  - Gif Delivery Network
  - Imgur
  - Reddit Galleries
  - Reddit Text Posts
  - Reddit Videos
  - Redgifs
  - YouTube
  - Streamable

## Contributing

If you wish to contribute, see [Contributing](docs/CONTRIBUTING.md) for more information.

When reporting any issues or interacting with the developers, please follow the [Code of Conduct](docs/CODE_OF_CONDUCT.md).
