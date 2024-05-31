#!/bin/bash

## Get NLDAS data from NOAA
python NLDAS_setup.py
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -i output_urls.txt

## Convert time coordinate
for f in *.nc; do
  echo $f
  ncks -O --mk_rec_dmn time $f $f
done

## Concatenate
ncrcat NLDAS_FORB0125*.nc cat.nc
rm -v NLDAS_FORB0125*.nc

## Extract NEUS box
ncks -d time,1996-01-15,1996-02-15 -d lat,42.,47. -d lon,-126.,-120. cat.nc sub.nc

mv -v sub.nc NLDAS-VIC4.0.5.v2.nc
rm -v cat.nc
