#!/bin/bash -l

# Script settings
merge_pngs=true
perform_analysis=true

######

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

set -e # Turn on error checking

## Make directories (note, the py files should do this for you)
#echo "Making directories..."
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

echo "Organizing statistics"
cd output
rm -vf supercat.csv
cat Events_*csv > supercat.TMP
mv -v supercat.TMP supercat.csv
cd ..

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

echo "Checking correlations"
python check_correlations.py
cd corr_stats
cat *offonee3smcorr.csv > corr_catted.csv
cd ..

echo "Creating histograms"
python histograms.py '-1.0'
python histograms.py '95.0'

echo "Computing annual stats"
python annual_stats.py

echo "NCL plotting"
ncl plot-climo.ncl 'var="SWE"'
ncl plot-climo.ncl 'var="dSWE"'
ncl plot-climo.ncl 'var="ROF"'
ncl plot-climo.ncl 'var="PRECIP"'

echo "1996 event comparison"
python compare-1996-event.py

echo "DONE!"