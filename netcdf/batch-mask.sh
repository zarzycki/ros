#!/bin/bash

ROSREPO="/scratch/cmz5202/ros/"

#####

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${ROSREPO}'"'
ncl mask_ncl.ncl 'model="L15"' 'repopath="'${ROSREPO}'"'
ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${ROSREPO}'"'
ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${ROSREPO}'"'
