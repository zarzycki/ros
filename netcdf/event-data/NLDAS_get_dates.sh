#!/bin/bash

# Get start and end dates from user input
start_date=$1
end_date=$2

# Convert dates to 'seconds since 1970-01-01' to use in the loop
start_sec=$(date -d "$start_date" +%s)
end_sec=$(date -d "$end_date" +%s)

echo $start_sec
echo $end_sec

# Define the output file
output_file="output_urls.txt"

# Ensure the output file is empty
> "$output_file"

# Loop over each day in the range
for (( d=$start_sec; d<=$end_sec; d+=86400 )); do
  # Get the current date in YYYYMMDD format
  current_date=$(date -d @"$d" +%Y%m%d)
  echo $current_date
  # Get the year and day of year for the URL
  year=$(date -d @"$d" +%Y)
  doy=$(date -d @"$d" +%j)

  # Loop over each hour
  for hour in {00..23}; do
    # Construct the URL
    url="https://data.gesdisc.earthdata.nasa.gov/data/NLDAS/NLDAS_FORB0125_H.2.0/$year/$doy/NLDAS_FORB0125_H.A${current_date}.${hour}00.020.nc"
    # Append the URL to the output file
    echo $url >> "$output_file"
  done
done

echo "URLs have been written to $output_file."

