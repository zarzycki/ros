#!/bin/bash -l

ROSREPO="/Users/cmz5202/Software/ros/"
BASINSHAPE="srb"
#BASINSHAPE="WillametteBasin"

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