#!/bin/sh

JOB_LINK="https\:\/\/www.linkedin.com\/jobs\/view\/"

JOB_TITLE="data%20engineer"
LOCATION="brazil"
URL="https://www.linkedin.com/jobs/search?keywords=${JOB_TITLE}&location=${LOCATION}"

dateAndTime=$(date -u +'%F %H-%M-%S %Z')
OUTPUT_FILE="../job-links/$dateAndTime.txt"

curl "$URL" | grep data-entity-urn  | sed "s/^.*urn:li:jobPosting:/$JOB_LINK/" | sed "s/\" data-search-id.*$//" >> "$OUTPUT_FILE"