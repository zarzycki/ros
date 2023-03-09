#!/bin/bash -l

PATHTOROSREPO=/Users/cmz5202/Software/ros/ros/

ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="L15"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${PATHTOROSREPO}'"'
