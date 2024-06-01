#!/bin/bash

RAWDIR="/Users/cmz5202/NetCDF/ros/"
ROSREPO="/Users/cmz5202/Software/ros/"

STARTYR=1985
ENDYR=2005

## SRB
MINLAT=39.0
MAXLAT=44.0
MINLON=-80.0
MAXLON=-74.0

## WillametteBasin
# MINLAT=42.0
# MAXLAT=47.0
# MINLON=-126.0
# MAXLON=-120.0

## California
# MINLAT=32.0
# MAXLAT=43.0
# MINLON=-128.0
# MAXLON=-113.0

######################################################################################

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

OUTDIR="$ROSREPO/netcdf/"

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