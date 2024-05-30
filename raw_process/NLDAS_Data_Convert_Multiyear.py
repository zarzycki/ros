#!/usr/bin/env python
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import sys
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('RAWDIR', type=str, help='The raw directory path')
parser.add_argument('outdir', type=str, help='The output directory path')
parser.add_argument('susslats_start', type=float, help='The start latitude for susslats')
parser.add_argument('susslats_end', type=float, help='The end latitude for susslats')
parser.add_argument('susslons_start', type=float, help='The start longitude for susslons')
parser.add_argument('susslons_end', type=float, help='The end longitude for susslons')
parser.add_argument('start_year', type=int, help='The start year for the data range')
parser.add_argument('end_year', type=int, help='The end year for the data range')

args = parser.parse_args()

RAWDIR = args.RAWDIR
outdir = args.outdir
start_year = args.start_year
end_year = args.end_year

print("RAWDIR:", RAWDIR)
print("outdir:", outdir)
print("start_year:", start_year)
print("end_year:", end_year)

years = np.arange(start_year, end_year + 1, 1); years = [str(i) for i in years]
'''
The range of years to be analyzed. Note that the last year in the range above is not included.
'''
latmin = args.susslats_start; latmax = args.susslats_end
lonmin = args.susslons_start; lonmax = args.susslons_end

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

