#!/bin/bash

RAWDIR="/Users/cmz5202/NetCDF/ros/"
ROSREPO="/Users/cmz5202/Software/ros/"
BASINSHAPE="srb"       # srb, WillametteBasin, SacRB_USGS1802, sierranevada

STARTYR=1985
ENDYR=2005

if [ "$BASINSHAPE" = "srb" ]; then
  MINLAT=39.0
  MAXLAT=44.0
  MINLON=-80.0
  MAXLON=-74.0
elif [ "$BASINSHAPE" = "WillametteBasin" ]; then
  MINLAT=42.0
  MAXLAT=47.0
  MINLON=-126.0
  MAXLON=-120.0
elif [ "$BASINSHAPE" = "SacRB_USGS1802" ]; then
  MINLAT=32.0
  MAXLAT=43.0
  MINLON=-128.0
  MAXLON=-113.0
elif [ "$BASINSHAPE" = "sierranevada" ]; then
  MINLAT=32.0
  MAXLAT=43.0
  MINLON=-128.0
  MAXLON=-113.0
else
  echo "Unknown BASINSHAPE: $BASINSHAPE"
  exit 1
fi

KEEP_MERGED=false
for arg in "$@"; do
  case $arg in
    --keep-merged)
      KEEP_MERGED=true
      shift # Remove --keep-merged from processing
      ;;
    *)
      # Unknown option
      ;;
  esac
done

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

OUTDIR="$ROSREPO/netcdf/"

echo "Creating merged netcdf files"

convert_data() {
  script=$1
  python $script "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
}

if [ "$force_serial" == "true" ] || ! command -v parallel > /dev/null; then
  echo "Running in serial mode."
  python JRA_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
  python E3SM_Data_Convert.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
  python NLDAS_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
  python L15_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
else
  echo "GNU Parallel is installed and not forced to serial. Running in parallel mode."
  export RAWDIR ROSREPO MINLAT MAXLAT MINLON MAXLON STARTYR ENDYR OUTDIR
  export -f convert_data
  parallel convert_data ::: \
    "JRA_Data_Convert_Multiyear.py" \
    "E3SM_Data_Convert.py" \
    "NLDAS_Data_Convert_Multiyear.py" \
    "L15_Data_Convert_Multiyear.py"
fi

cd $OUTDIR
echo "Masking files"

run_ncl() {
  model=$1
  ncl mask_ncl.ncl 'model="'${model}'"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
}

if [ "$force_serial" == "true" ] || ! command -v parallel > /dev/null; then
  echo "Running in serial mode."
  ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
  ncl mask_ncl.ncl 'model="L15"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
  ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
  ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
else
  echo "GNU Parallel is installed and not forced to serial. Running in parallel mode."
  export ROSREPO BASINSHAPE
  # Load env_parallel to export environment variables
  source $(which env_parallel.bash)
  export -f run_ncl
  env_parallel run_ncl ::: "NLDAS" "L15" "E3SM" "JRA"
fi

if [ "$KEEP_MERGED" = false ]; then
  echo "Deleting unmasked files"
  rm -v *_merged.nc
else
  echo "--keep-merged option detected, not deleting unmasked files"
fi

# Loop over files ending in _masked.nc and rename them
for file in *_masked.nc; do
  if [ -f "$file" ]; then
    new_name="${file%.nc}_${BASINSHAPE}.nc"
    mv "$file" "$new_name"
    echo "Renamed $file to $new_name"
  fi
done