#!/bin/bash -l

# Script settings
USGS_gauge="01570500"      # 01570500 for SRB, 14211720 for Willamette
merge_pngs=true
perform_analysis=true
auto_domain_climo=true     # false to reproduce SRB domain, true otherwise
force_purge=true

######

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

force_serial=false
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --force_serial)
      force_serial=true
      shift # past argument
      ;;
    *)    # unknown option
      shift # past argument
      ;;
  esac
done

if [ "$force_purge" == "true" ]; then
  rm -vrf output/*
  rm -vrf climo/*
  rm -vrf corr_stats/*
  rm -vrf hists/*
fi

set -e # Turn on error checking

if [ "$perform_analysis" == "true" ]; then
  echo "Doing analysis..."
  analyses=(
    "L15 -1 $USGS_gauge"
    "NLDAS -1 $USGS_gauge"
    "JRA -1 $USGS_gauge"
    "E3SM -1 $USGS_gauge"
    "L15 95 $USGS_gauge"
    "NLDAS 95 $USGS_gauge"
    "JRA 95 $USGS_gauge"
    "E3SM 95 $USGS_gauge"
  )

  run_analysis() {
    args=$1
    python analysis.py $args
  }

  if [ "$force_serial" == "true" ] || ! command -v parallel > /dev/null; then
    echo "Running in serial mode."
    for analysis in "${analyses[@]}"; do
      run_analysis "$analysis"
    done
  else
    echo "GNU Parallel is installed and not forced to serial. Running in parallel mode."
    export -f run_analysis
    parallel run_analysis ::: "${analyses[@]}"
  fi
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

  figtypes=("SWE" "events" "scatplot")

  mkdir -p ./merged/

  # Function to merge at the YYYY level
  merge_png() {
    YYYY=$1
    figtype=$2
    DPI=500
    echo "Merging $YYYY for $figtype"
    convert +append -density ${DPI} L15_${YYYY}_${figtype}.pdf NLDAS_${YYYY}_${figtype}.pdf tmp1_${YYYY}_${figtype}.png
    convert +append -density ${DPI} JRA_${YYYY}_${figtype}.pdf E3SM_${YYYY}_${figtype}.pdf tmp2_${YYYY}_${figtype}.png
    convert -append tmp1_${YYYY}_${figtype}.png tmp2_${YYYY}_${figtype}.png tmp3_${YYYY}_${figtype}.png
    mv tmp3_${YYYY}_${figtype}.png ./merged/merged_${figtype}_${YYYY}.png
    rm -v tmp?_${YYYY}_${figtype}.png
  }

  if [ "$force_serial" == "true" ] || ! command -v parallel > /dev/null; then
    echo "Running in serial mode."
    for YYYY in {1984..2005}; do
      for figtype in "${figtypes[@]}"; do
        merge_png $YYYY $figtype
      done
    done
  else
    echo "GNU Parallel is installed and not forced to serial. Running in parallel mode."
    export -f merge_png
    export DPI
    parallel merge_png ::: {1984..2005} ::: "${figtypes[@]}"
  fi

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
ncl plot-climo.ncl 'var="SWE"' 'auto_domain_climo="'$auto_domain_climo'"'
ncl plot-climo.ncl 'var="dSWE"' 'auto_domain_climo="'$auto_domain_climo'"'
ncl plot-climo.ncl 'var="ROF"' 'auto_domain_climo="'$auto_domain_climo'"'
ncl plot-climo.ncl 'var="PRECIP"' 'auto_domain_climo="'$auto_domain_climo'"'

echo "1996 event comparison"
python compare-1996-event.py

echo "DONE!"