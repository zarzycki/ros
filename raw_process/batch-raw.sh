#!/bin/bash -l

conda activate ros-metrics

RAWDIR="/storage/group/cmz5202/default/ros/"
OUTDIR="/scratch/cmz5202/ros/netcdf/"

python JRA_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
python E3SM_Data_Convert.py ${RAWDIR} ${OUTDIR}
python NLDAS_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
python L15_Data_Convert_Multiyear.py ${RAWDIR} ${OUTDIR}
