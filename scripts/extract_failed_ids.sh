#!/bin/bash

if [ -e "$1" ]; then
    file="$1"
else
    echo 'CANNOT FIND LOG FILE'
    exit 1
fi

if [ -n "$2" ]; then
    output="$2"
    echo "Outputting IDs to $output"
else
    output="failed.txt"
fi

grep 'Could not download submission' "$file" | awk '{ print $12 }' | rev | cut -c 2- | rev >>"$output"
grep 'Failed to download resource' "$file" | awk '{ print $15 }' >>"$output"
