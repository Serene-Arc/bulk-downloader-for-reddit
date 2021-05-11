#!/bin/bash

if [ -e "$1" ]; then
    file="$1"
else
    echo 'CANNOT FIND LOG FILE'
    exit 1
fi

echo "Downloaded submissions: $( grep -c 'Downloaded submission' "$file" )"
echo "Failed downloads: $( grep -c 'failed to download submission' "$file" )"
echo "Files already downloaded: $( grep -c 'already exists, continuing' "$file" )"
echo "Hard linked submissions: $( grep -c 'Hard link made' "$file" )"
echo "Excluded submissions: $( grep -c 'in exclusion list' "$file" )"
echo "Files with existing hash skipped: $( grep -c 'downloaded elsewhere' "$file" )"
echo "Submissions from excluded subreddits: $( grep -c 'in skip list' "$file" )"
