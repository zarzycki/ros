#!/bin/bash

## Get NLDAS data from NOAA
python setup.py
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -i subset_NLDAS_FORB0125_H_2.0_20230722_132203_.txt

## Convert time coordinate
for f in *.nc; do
  echo $f
  ncks -O --mk_rec_dmn time $f $f
done

## Concatenate
ncrcat NLDAS_FORB0125*.nc cat.nc

## Extract NEUS box
ncks -d time,1996-01-01,1996-02-01 -d lat,38.,45. -d lon,-80.,-74. cat.nc sub.nc
