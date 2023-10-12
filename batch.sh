#!/bin/bash -l

conda activate ros-metrics

# Script settings
merge_pngs=true
perform_analysis=true

set -e

## Make directories
echo "Making directories..."
#mkdir -p ./output
#mkdir -p ./corr_stats

if [ "$perform_analysis" == "true" ]; then
  echo "Doing analysis..."
  # Absolute
  python analysis.py L15 -1
  python analysis.py NLDAS -1
  python analysis.py JRA -1
  python analysis.py E3SM -1
  # Normalized
  python analysis.py L15 95
  python analysis.py NLDAS 95
  python analysis.py JRA 95
  python analysis.py E3SM 95
fi

## create supercat
echo "Organizing statistics"
cd output
rm -vf supercat.csv
cat Events_*csv > supercat.TMP
mv -v supercat.TMP supercat.csv
cd ..

## Created merged pngs
if [ "$merge_pngs" == "true" ]; then
  echo "Creating merged PNGs"
  cd output
  mkdir -p ./merged/
  DPI=500
  figtypes=("SWE" "events" "scatplot")
  for YYYY in {1984..2005}; do
    echo "Merging $YYYY"
    for figtype in "${figtypes[@]}"; do
      convert +append -density ${DPI} L15_${YYYY}_${figtype}.pdf NLDAS_${YYYY}_${figtype}.pdf tmp1.png
      convert +append -density ${DPI} JRA_${YYYY}_${figtype}.pdf E3SM_${YYYY}_${figtype}.pdf tmp2.png
      convert -append tmp1.png tmp2.png tmp3.png
      mv tmp3.png ./merged/merged_${figtype}_${YYYY}.png
      rm tmp*.png
    done
  done
  cd ..
fi

echo "Check correlations"
python check_correlations.py
cd corr_stats
cat *offonee3smcorr.csv > corr_catted.csv
cd ..

echo "Histograms"
python histograms.py '-1.0'
python histograms.py '95.0'

echo "Compute annaul stats"
python annual_stats.py

echo "NCL plotting"
ncl plot-climo.ncl 'var="SWE"'
ncl plot-climo.ncl 'var="dSWE"'
ncl plot-climo.ncl 'var="ROF"'
ncl plot-climo.ncl 'var="PRECIP"'

echo "1996 event comparison"
python compare-1996-event.py

echo "DONE"