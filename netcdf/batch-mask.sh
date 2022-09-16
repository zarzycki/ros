#!/bin/bash

PATHTOROSREPO=/Users/colin/Software/ros/

ncl mask_ncl.ncl 'model="NLDAS"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="L15"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="E3SM"' 'repopath="'${PATHTOROSREPO}'"'
ncl mask_ncl.ncl 'model="JRA"' 'repopath="'${PATHTOROSREPO}'"'