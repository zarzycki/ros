#!/bin/bash -l

conda activate ros-metrics

set -e

python analysis.py L15 -1
python analysis.py NLDAS -1
python analysis.py JRA -1
python analysis.py E3SM -1

python analysis.py L15 95
python analysis.py NLDAS 95
python analysis.py JRA 95
python analysis.py E3SM 95

## create supercat
cd output
cat *csv > supercat.TMP
mv supercat.TMP supercat.csv
cd ..

## check correlations
python check_correlations.py
cd corr_stats
cat *offonee3smcorr.csv > corr_catted.csv
cd ..

## Do histograms
python histograms.py '-1.0'
python histograms.py '95.0'

## get climatological means
ncl plot-climo.ncl 'var="SWE"'
ncl plot-climo.ncl 'var="dSWE"'
ncl plot-climo.ncl 'var="ROF"'
ncl plot-climo.ncl 'var="PRECIP"'
