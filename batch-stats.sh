#!/bin/bash -l

# Script settings
USGS_gauge="01570500"   # 01570500 for SRB, 14211720 for Willamette, 11425500 for SacRiver
BASINSHAPE="srb"        # srb, WillametteBasin, SacRB_USGS1802
auto_domain_climo=false  # false to reproduce SRB domain, true otherwise
merge_pngs=true
perform_analysis=true
force_purge=true

######################################################################################

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

OUTPUTDIR="./output/$BASINSHAPE/"

if [ "$force_purge" == "true" ]; then
  rm -vrf $OUTPUTDIR
fi

set -e # Turn on error checking

if [ "$perform_analysis" == "true" ]; then
  echo "Doing analysis..."
  analyses=(
    "L15 -1 $USGS_gauge $BASINSHAPE"
    "NLDAS -1 $USGS_gauge $BASINSHAPE"
    "JRA -1 $USGS_gauge $BASINSHAPE"
    "E3SM -1 $USGS_gauge $BASINSHAPE"
    "L15 95 $USGS_gauge $BASINSHAPE"
    "NLDAS 95 $USGS_gauge $BASINSHAPE"
    "JRA 95 $USGS_gauge $BASINSHAPE"
    "E3SM 95 $USGS_gauge $BASINSHAPE"
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
pushd "$OUTPUTDIR/csv/"
rm -vf supercat.csv
cat Events_*csv > supercat.TMP
mv -v supercat.TMP supercat.csv
popd

if [ "$merge_pngs" == "true" ]; then
  echo "Creating merged PNGs"
  pushd "$OUTPUTDIR/annual_plots/"

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

  popd
fi

echo "Checking correlations"
python check_correlations.py $BASINSHAPE
pushd "$OUTPUTDIR/corr_stats"
cat *offonee3smcorr.csv > corr_catted.csv
popd

echo "Creating histograms"
python histograms.py '-1.0' $BASINSHAPE
python histograms.py '95.0' $BASINSHAPE

echo "Computing annual stats"
python annual_stats.py $BASINSHAPE

echo "NCL plotting"
ncl plot-climo.ncl 'var="SWE"' 'auto_domain_climo="'$auto_domain_climo'"' 'basinshape="'$BASINSHAPE'"'
ncl plot-climo.ncl 'var="dSWE"' 'auto_domain_climo="'$auto_domain_climo'"' 'basinshape="'$BASINSHAPE'"'
ncl plot-climo.ncl 'var="ROF"' 'auto_domain_climo="'$auto_domain_climo'"' 'basinshape="'$BASINSHAPE'"'
ncl plot-climo.ncl 'var="PRECIP"' 'auto_domain_climo="'$auto_domain_climo'"' 'basinshape="'$BASINSHAPE'"'

echo "Event comparison"
python compare-event.py $BASINSHAPE

echo "DONE!"