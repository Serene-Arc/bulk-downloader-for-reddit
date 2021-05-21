# Useful Scripts

Due to the verboseness of the logs, a great deal of information can be gathered quite easily from the BDFR's logfiles. In this folder, there is a selection of scripts that parse these logs, scraping useful bits of information. Since the logfiles are recurring patterns of strings, it is a fairly simple matter to write scripts that utilise tools included on most Linux systems.

  - [Script to extract all successfully downloaded IDs](#extract-all-successfully-downloaded-ids)
  - [Script to extract all failed download IDs](#extract-all-failed-ids)
  - [Timestamp conversion](#converting-bdfrv1-timestamps-to-bdfrv2-timestamps)
  - [Printing summary statistics for a run](#printing-summary-statistics)

## Extract all Successfully Downloaded IDs

This script is contained [here](extract_successful_ids.sh) and will result in a file that contains the IDs of everything that was successfully downloaded without an error. That is, a list will be created of submissions that, with the `--exclude-id-file` option, can be used so that the BDFR will not attempt to redownload these submissions/comments. This is likely to cause a performance increase, especially when the BDFR run finds many resources.

The script can be used with the following signature:

```bash
./extract_successful_ids.sh LOGFILE_LOCATION <OUTPUT_FILE>
```

By default, if the second argument is not supplied, the script will write the results to `successful.txt`.

An example of the script being run on a Linux machine is the following:

```bash
./extract_successful_ids.sh ~/.config/bdfr/log_output.txt
```

## Extract all Failed IDs

[This script](extract_failed_ids.sh) will output a file of all IDs that failed to be downloaded from the logfile in question. This may be used to prevent subsequent runs of the BDFR from re-attempting those submissions if that is desired, potentially increasing performance.
The script can be used with the following signature:

```bash
./extract_failed_ids.sh LOGFILE_LOCATION <OUTPUT_FILE>
```

By default, if the second argument is not supplied, the script will write the results to `failed.txt`.

An example of the script being run on a Linux machine is the following:

```bash
./extract_failed_ids.sh ~/.config/bdfr/log_output.txt
```

## Converting BDFRv1 Timestamps to BDFRv2 Timestamps

BDFRv2 uses an internationally recognised and standardised format for timestamps, namely ISO 8601. This is highly recommended due to the nature of using such a widespread and understood standard. However, the BDFRv1 does not use this standard. Due to this, if you've used the old timestamp in filenames or folders, the BDFR will no longer recognise them as the same file and potentially redownload duplicate resources.

To prevent this, it is recommended that you rename existing files to ISO 8601 standard. This can be done using the [timestamp-converter](https://github.com/Serene-Arc/timestamp-converter) tool made for this purpose. Instructions specifically for the BDFR are available in that project.

## Printing Summary Statistics

A simple script has been included to print sumamry statistics for a run of the BDFR. This is mainly to showcase how easy it is to extract statistics from the logfiles. You can extend this quite easily. For example, you can print how often the Imgur module is used, or how many 404 errors there are in the last run, or which module has caused the most errors. The possibilities really are endless.

```bash
./print_summary.sh LOGFILE_LOCATION
```

This will create an output like the following:

```
Downloaded submissions: 250
Failed downloads: 103
Files already downloaded: 20073
Hard linked submissions: 30
Excluded submissions: 1146
Files with existing hash skipped: 0
Submissions from excluded subreddits: 0
```
