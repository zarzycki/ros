#!/bin/bash

RAWDIR="/storage/group/cmz5202/default/ros/"
ROSREPO="/scratch/cmz5202/ros/"

#####

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

OUTDIR="$ROSREPO/netcdf/"
python JRA_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
python E3SM_Data_Convert.py ${RAWDIR} ${OUTDIR}
python NLDAS_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
python L15_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
