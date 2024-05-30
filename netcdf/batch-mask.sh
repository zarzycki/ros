#!/bin/bash -l

ROSREPO="/Users/cmz5202/Software/ros/"
BASINSHAPE="srb"
#BASINSHAPE="WillametteBasin"

#####

## Initialize conda and load env
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"
conda activate ros-metrics

ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
ncl mask_ncl.ncl 'model="L15"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${ROSREPO}'"' 'basinshape="'${BASINSHAPE}'"'
