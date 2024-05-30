#!/bin/bash

RAWDIR="/Users/cmz5202/NetCDF/ros/"
ROSREPO="/Users/cmz5202/Software/ros/"

#####

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

STARTYR=1985
ENDYR=2005

## SRB
MINLAT=39.0
MAXLAT=44.0
MINLON=-80.0
MAXLON=-74.0

## California
# MINLAT=32.0
# MAXLAT=42.0
# MINLON=-128.0
# MAXLON=-113.0

## WillametteBasin
# MINLAT=42.0
# MAXLAT=47.0
# MINLON=-126.0
# MAXLON=-120.0

OUTDIR="$ROSREPO/netcdf/"

python JRA_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
python E3SM_Data_Convert.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
python NLDAS_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"
python L15_Data_Convert_Multiyear.py "$RAWDIR" "$OUTDIR" "$MINLAT" "$MAXLAT" "$MINLON" "$MAXLON" "$STARTYR" "$ENDYR"