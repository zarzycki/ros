# Get observational data

### E3SM

Using the nudged runs:

```
start_date=1996-01-01
end_date=1996-02-01
lat_min=38.0
lat_max=45.0
lon_min=-80.0
lon_max=-74.0

data_dir="/storage/home/cmz5202/group/NDG-ne30-ERA5-N58/atm/hist/"
map_file="/storage/home/cmz5202/work/maps/hyperion/map_ne30np4_to_1.0x1.0_CONUS.nc"

# Compute required dates
start_prev_month=$(date -d "$start_date -1 month" +%Y-%m)
start_month=$(date -d "$start_date" +%Y-%m)
end_month=$(date -d "$end_date" +%Y-%m)
end_next_month=$(date -d "$end_date +1 month" +%Y-%m)

echo $start_prev_month
echo $start_month
echo $end_month
echo $end_next_month

cd $data_dir
ncrcat NDG-ne30-ERA5-N58.eam.h5.${start_prev_month}-??-00000.nc \
       NDG-ne30-ERA5-N58.eam.h5.${start_month}-??-00000.nc \
       NDG-ne30-ERA5-N58.eam.h5.${end_month}-??-00000.nc \
       NDG-ne30-ERA5-N58.eam.h5.${end_next_month}-??-00000.nc \
       E3SM-catted-native.nc

# Remap the data
ncremap -i E3SM-catted-native.nc -o E3SM-catted-native_regrid.nc -m "$map_file"

# Subset data
ncks -d time,"$start_date","$end_date" -d lat,$lat_min,$lat_max -d lon,$lon_min,$lon_max E3SM-catted-native_regrid.nc tmp.nc

# Rename and clean up
mv -v tmp.nc E3SM-catted-native_regrid.v2.nc
rm -v E3SM-catted-native.nc E3SM-catted-native_regrid.nc
```

### L15

Data acquired from FTP server, for example.

```
ftp://livnehpublicstorage.colorado.edu/public/Livneh.2013.CONUS.Dataset/Derived.Subdaily.Outputs.asc.v.1.2.1915.2011.bz2/fluxes.125.120.37.49/VIC_subdaily_fluxes_Livneh_CONUSExt_v.1.2_2013_44.90625_-123.03125.bz2
```

Find nearest lat/lon point to station of interest and pull.

### NLDAS

```
# Build dates to download
bash NLDAS_get_dates.sh 1996-01-15 1996-02-15
# Download (will be prompted for EarthData credentials)
bash NLDAS_process.sh 
```

### JRA

### obs

Get data from `https://mesonet.agron.iastate.edu/request/download.phtml`.

Find relevant station for the ASOS network, select the date range, request all variables in CSV format. Download.

The CSV header should read:

```
station,valid,tmpf,dwpf,relh,drct,sknt,p01i,alti,mslp,vsby,gust,skyc1,skyc2,skyc3,skyc4,skyl1,skyl2,skyl3,skyl4,wxcodes,ice_accretion_1hr,ice_accretion_3hr,ice_accretion_6hr,peak_wind_gust,peak_wind_drct,peak_wind_time,feel,metar,snowdepth
CXY,1996-01-01 00:00,36.00,32.00,85.37,360.00,5.00,M,29.96,M,3.00,M,SCT,BKN,OVC,   ,4000.00,6000.00,10000.00,M,M,M,M,M,M,M,M,31.10,KCXY 010000Z 36005KT 3SM DZ SCT040 BKN060 OVC100 02/00 A2996 RMK SLPNO T00220000,M
CXY,1996-01-01 01:00,36.86,32.00,82.38,180.00,6.00,M,29.96,M,5.00,M,OVC,   ,   ,   ,6000.00,M,M,M,M,M,M,M,M,M,M,31.38,KCXY 010100Z 18006KT 5SM DZ OVC060 03/00 A2996 RMK SLPNO T00270000,M
```
