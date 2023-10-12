#!/usr/bin/env python
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import sys

## Command line args
## Note, sys.arg[0] is the name of the function
print ("Number of arguments: ", len(sys.argv))
print ("The arguments are: " , str(sys.argv))
RAWDIR = sys.argv[1]
outdir= sys.argv[2]


years = np.arange(1985, 2006, 1); years = [str(i) for i in years]
'''
The range of years to be analyzed. Note that the last year in the range above is not included.
'''
latmin = 39.0; latmax = 44.0
lonmin = -80.0; lonmax = -74.0



'''
Latitude and longitude can be modified to other areas
'''

def get_suss(vic, forcing, latrange, lonrange):
    susslats = forcing["lat_110"].sel(lat_110 = latrange).values;
    susslons = forcing["lon_110"].sel(lon_110 = lonrange).values
    precip = 24*forcing["A_PCP_110_SFC_acc1h"].sel(lat_110 = susslats, lon_110 = susslons)
    precip = precip.sel(lat_110 = susslats, lon_110 = susslons).values
    runoff = 24*vic["SSRUN_GDS0_SFC_acc1h"].sel(g0_lat_0 = np.round(susslats, 3), g0_lon_1 = susslons).values
    base = 24*vic["BGRUN_GDS0_SFC_acc1h"].sel(g0_lat_0 = np.round(susslats, 3), g0_lon_1 = susslons).values
    '''
    The multiplication by 24 is because the values given by the dataset are 1-hour means.
    '''
    swe = vic["WEASD_GDS0_SFC"].sel(g0_lat_0 = np.round(susslats, 3), g0_lon_1 = susslons).values

    trans = vic["WEASD_GDS0_SFC"].sel(g0_lat_0 = np.round(susslats, 3), g0_lon_1 = susslons).values
    et = 24*vic["EVP_GDS0_SFC_acc1h"].sel(g0_lat_0 = np.round(susslats, 3), g0_lon_1 = susslons).values
    et = et + trans

    times = forcing["time"].values
    sussdata = xr.Dataset({"PRECIP": (("time", "lat", "lon"), precip), "SWE": (("time", "lat", "lon"), swe), "ROF": (("time", "lat", "lon"), runoff),
                          "BASE": (("time", "lat", "lon"), base), "ET": (("time", "lat", "lon"), et)
                          },
                         {"time": ("time", times), "lat": susslats, "lon": susslons})
    return sussdata
'''
This function returns a dataset with daily mean precipitation, runoff, and SWE. It doesn't yet contain dSWE, which
is created in the function below.
'''

def get_dswe(data, latrange, lonrange):
    susslats = data["lat"].sel(lat = latrange).values; susslons = data["lon"].sel(lon = lonrange).values
    times = data["time"][1::].values
    dswe = [data["SWE"].isel(time = i+1)-data["SWE"].isel(time = i) for i in range(len(times))]
    '''
    Note that, even though "times" is defined as starting from the second entry, the SWE data is called using the
    "time" field from the original dataset. However, the index is set using "times", allowing i+1 to work without
    causing an OBOE.
    '''
    dswedata = xr.Dataset({"dSWE": (("time", "lat", "lon"), dswe)},
                          {"time": ("time", times), "lat": susslats, "lon": susslons})
    combdata = xr.merge([data.sel(time = times), dswedata])
    return combdata
'''
This function adds a dSWE parameter to the dataset established above. Note that, since dSWE is a comparative term,
it necessarily removes the first day of data, since there's nothing to compare SWE to at that point.
'''

months = [str(i).zfill(2) for i in range(1,13)]; print(months)
latrange = slice(latmin, latmax); lonrange = slice(lonmin, lonmax);
ysusslist = []
for year in years:
    print("Getting "+year)
    susslist = []
    for month in months:
        ffile = RAWDIR+"/NLDAS-VIC/NLDAS_2_FORCING_"+year+month+".nc"
        forcing = xr.open_dataset(ffile);
        vfile = RAWDIR+"/NLDAS-VIC/NLDAS_2_VIC_"+year+month+".nc"
        vic = xr.open_dataset(vfile)
        sussdata = get_suss(vic, forcing, latrange, lonrange)
        susslist.append(sussdata)
    sussdata = xr.concat(susslist, dim = "time")
    ysusslist.append(sussdata)
yeardata = xr.concat(ysusslist, dim = "time")
yeardata = get_dswe(yeardata, latrange, lonrange)
'''
This creates a dataset containing daily averaged runoff and SWE, 24-hour accumulated precipitation, and 24-hour
change in SWE. Note that the get_dswe function is not called until all months and years of data have been marged.
This is because the get_dSWE function eliminates the first day of the dataset in its argument. Having the function
run on the full merged dataset rather than individual months prevents the first day of each month from being dropped.
'''


if not os.path.exists(outdir):
    os.mkdirs(outdir)
startyear = years[0]; endyear = years[-1]
yeardata.to_netcdf(outdir+"/NLDAS_"+startyear+"to"+endyear+"_merged.nc")
'''
This saves the dataset in the NLDAS directory. After the file is saved, this program shouldn't be run again unless
some aspect of the dataset (latitude, longitude, time period) is being changed.
'''

