#!/bin/bash -l

conda activate ros-metrics2

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
rm -vf supercat.csv
cat Events_*csv > supercat.TMP
mv supercat.TMP supercat.csv
cd ..

## Created merged pngs
cd output
mkdir -p ./merged/
DPI=500
figtypes=("SWE" "events" "scatplot")
for YYYY in {1984..2005}; do
  for figtype in "${figtypes[@]}"; do
  convert +append -density ${DPI} L15_${YYYY}_${figtype}.pdf NLDAS_${YYYY}_${figtype}.pdf tmp1.png
  convert +append -density ${DPI} JRA_${YYYY}_${figtype}.pdf E3SM_${YYYY}_${figtype}.pdf tmp2.png
  convert -append tmp1.png tmp2.png tmp3.png
  mv tmp3.png ./merged/merged_${figtype}_${YYYY}.png
  rm tmp*.png
  done
done
cd ..

## check correlations
python check_correlations.py
cd corr_stats
cat *offonee3smcorr.csv > corr_catted.csv
cd ..

## Do histograms
python histograms.py '-1.0'
python histograms.py '95.0'

python annual_stats.py

## get climatological means
ncl plot-climo.ncl 'var="SWE"'
ncl plot-climo.ncl 'var="dSWE"'
ncl plot-climo.ncl 'var="ROF"'
ncl plot-climo.ncl 'var="PRECIP"'

python compare-1996-event.py