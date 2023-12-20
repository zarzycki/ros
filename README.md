# ros-metrics

Create environment:

```
conda env create -n ros-metrics --file environment.yml   ### or mamba
conda activate ros-metrics

## To delete if needed
# Current:
# conda remove -n ros-metrics --all
# Deprecated:
# conda env remove -n ros-metrics
```

NOTE: Currently the repository requires NCL to mask the basin and create some climatology plots. NCL does not compile natively on Apple Silicon. If you must use such a system, the current solution is to install and x86_64 compatible NCL using Rosetta or otherwise outside of conda/mamba. If you do so, either comment out the NCL line from `environment.yml` or uninstall NCL from the conda environment created above to remove conflicts.

```
conda activate ros-metrics
conda uninstall ncl  ### or mamba
```


## Instructions

The instructions assume you are in the top level of the ROS repo. `ROSREPO` defines this location.

### 1. Create "merged" files from raw climate data

```
cd $ROSREPO/raw-process
# Set ROSREPO and RAWDIR in batch-raw.sh
./batch-raw.sh
cd ..
```

This will create four files in the "netcdf" subfolder of the repo with the "merged" datafiles over the SRB.

### 2. Mask "merged" files


```
cd $ROSREPO/netcdf
# Set ROSREPO
./batch-mask.ncl
cd ..
```

This will create four additional files in the "netcdf" subfolder of the repo, but with the data masked over the river basin.

**NOTE**: If NCL is keeping "zero" values after masking, ex:

```
(0)	487 data values kept
(0)	shapefile_mask_data: elapsed time: 11.6067 CPU seconds.
```

this is probably due to a version of NCL shipped with conda. I'm sure there are more clever solutions, but the hack is to flip the x/y calls on lines 240-241 of `ncl_utils/shapefile_utils.ncl`. See [NCL-list post](https://mailman.ucar.edu/pipermail/ncl-talk/2021-January/017775.html).

### 3. Run statistics

```
$ROSREPO/batch-stats.sh
```

There are a couple bools at the top of the script.

- `merge_pngs` takes the single panel outputs and merges to 2x2 png panels for visualization, although this isn't used in the paper
- `perform_analysis` decides whether the analysis to extract the ROS events should actually take place. This needs to be true if you haven't done so already, but since this is the most expensive part of the code, it makes sense to have a T/F switch.

## Repository notes:

Zenodo requires less than 100 files, so we need to tar many of the outputs (PDF and CSV files).

```
cd $ROSREPO

cd corr_stats/
tar -zcvf csv_correlations.tar.gz *.csv ; rm -v *.csv
cd ..

cd output/
tar -zcvf SWE_events_scatplot_figs.tar.gz *.pdf ; rm -v *.pdf
tar -zcvf csv_files_output.tar.gz *.csv ; rm -v *.csv
cd ..

cd hists/
tar -zcvf histograms_pdf.tar.gz *.pdf ; rm -v *.pdf
cd ..
```

We can untar with:

```
cd corr_stats/
tar -xvf csv_correlations.tar.gz
rm -v *.tar.gz
cd ..

cd output/
tar -xvf SWE_events_scatplot_figs.tar.gz
tar -xvf csv_files_output.tar.gz
rm -v *.tar.gz
cd ..

cd hists/
tar -xvf histograms_pdf.tar.gz
rm -v *.tar.gz
cd ..
```

To zip up the folder for Zenodo upload:

```
zip -r ros.zip ./ros/ -x '*.git*' -x '.DS_Store'
```
