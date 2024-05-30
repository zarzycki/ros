#!/bin/bash

### Usage: ./get-gauge-data.sh 11425500

# 01570500 - Harrisburg/SQ
# 14211720 - Willamette/Portland
# 11425500 - Sacramento River

if [ -z "$1" ]; then
  echo "Error: No USGS gauge ID (integer) provided."
  echo "Usage: $0 <gauge_id>"
  exit 1
fi

STATIONID=$1

################################################

## Figure out what sed command we have
if command -v gsed >/dev/null 2>&1; then
  sed_cmd="gsed"
else
  sed_cmd="sed"
fi

rm -v "$STATIONID.txt"
wget "https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=${STATIONID}&legacy=&referred_module=sw&period=&begin_date=1985-01-01&end_date=2005-12-31" -O tmp.txt
$sed_cmd -i '/^5s/d' tmp.txt
mv -v tmp.txt "$STATIONID.txt"
