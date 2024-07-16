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

An example of setting these folders follows:

```
ROSREPO="/Users/cmz5202/Software/ros/"
RAWDATA="/Users/cmz5202/NetCDF/ros/"
```

### 1. Create "merged" and "masked" files from raw climate data

```
cd $ROSREPO/raw_process
bash batch-raw.sh $ROSREPO $RAWDATA "srb"
cd ..
```

This will create four files in the "netcdf" subfolder of the repo with the "merged" datafiles over the SRB.

To generate a merged file over a different CONUS basin, adjust the lat/lon settings in `batch-raw.sh`. An example for the Willamette Basin is included (but commented out). Note the longitude convention of negative values representing "degrees west."

This will create four additional files in the "netcdf" subfolder of the repo, but with the data masked over the SRB (`BASINSHAPE="srb"`)

To generate masked files for a different basin, first put a set of shapefiles in a unique subdirectory under the "shapes" directory. Then update `batch-mask.sh` to point to this using the `BASINSHAPE` variable. `WillametteBasin` is commented out but included as an example.

An example of calling the script with additional basins:

```
cd $ROSREPO/raw_process
bash batch-raw.sh $ROSREPO $RAWDATA "WillametteBasin"
bash batch-raw.sh $ROSREPO $RAWDATA "SacRB_USGS1802"
cd ..
```

**NOTE**: If NCL is keeping "zero" values after masking, ex:

```
(0)	487 data values kept
(0)	shapefile_mask_data: elapsed time: 11.6067 CPU seconds.
```

this is probably due to a version of NCL shipped with conda. I'm sure there are more clever solutions, but the hack is to flip the x/y calls on lines 240-241 of `ncl_utils/shapefile_utils.ncl`. See [NCL-list post](https://mailman.ucar.edu/pipermail/ncl-talk/2021-January/017775.html).

### 2. Run statistics

```
bash $ROSREPO/batch-stats.sh
```

There are a few settings at the top of the script.

- `USGS_gauge` specifies the USGS number of a relevant gauge over the requested time period with daily streamflow data (used for plotting purposes only). To acquire gauge data, see the `./data` subfolder and the associated shell script.
- `BASINSHAPE` this is the name of the basin that will be evaluated. This basin must have been masked by step #1.
- `auto_domain_climo` set to true will tell the NCL code that plots the climatology to use the min/max coordinates from the merged domain (from `batch-raw.sh`) when plotting. Setting to FALSE allows the user to specify the actual min/max coordinates in the NCL code (FALSE reproduces the SRB results from Zarzycki et al., NHESS, 2024).
- `merge_pngs` takes the single panel outputs and merges to 2x2 png panels for visualization, although this isn't used in the paper
- `perform_analysis` decides whether the analysis to extract the ROS events should actually take place. This needs to be true if you haven't done so already, but since this is the most expensive part of the code, it makes sense to have a T/F switch.
- `force_purge` set to true will delete all existing analysis files (e.g., statistics, images, etc.). It will not purge merged or masked NetCDF files.
- `UQSTR` provides a "unique string" that will be appended to the basin name in the output directory tree. This is useful for sensitivity runs or other situations where you don't want to archive an output set under the "default" shapefile folder.

#### Automated tip

You can edit the top of `batch-stats.sh` to take command line args:

```
USGS_gauge=$2
BASINSHAPE=$3
auto_domain_climo=$1
merge_pngs=true
perform_analysis=true
force_purge=true
UQSTR=$4
```

and then run multiple versions of the code:

```
bash batch-stats.sh false "01570500" "srb" ""
bash batch-stats.sh true "14211720" "WillametteBasin" ""
bash batch-stats.sh true "11425500" "SacRB_USGS1802" ""
bash batch-stats.sh false "01570500" "srb" "F14"
```


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
