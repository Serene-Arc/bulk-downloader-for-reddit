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
    output="./successful.txt"
fi

{
    grep 'Downloaded submission' "$file" | awk '{ print $(NF-2) }' ;
    grep 'Resource hash' "$file" | awk '{ print $(NF-2) }' ;
    grep 'Download filter' "$file" | awk '{ print $(NF-3) }' ;
    grep 'already exists, continuing' "$file" | awk '{ print $(NF-3) }' ;
    grep 'Hard link made' "$file" | awk '{ print $(NF) }' ;
} >> "$output"
