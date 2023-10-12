#!/bin/bash -l

PATHTOROSREPO=/scratch/cmz5202/ros/

conda activate ros-metrics

ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="L15"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${PATHTOROSREPO}'"'
