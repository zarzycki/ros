#!/usr/bin/env python
import os
import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import argparse

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
susslats = slice(args.susslats_start, args.susslats_end)
susslons = slice(args.susslons_start, args.susslons_end)
start_year = args.start_year
end_year = args.end_year

print("RAWDIR:", RAWDIR)
print("outdir:", outdir)
print("susslats:", susslats)
print("susslons:", susslons)
print("start_year:", start_year)
print("end_year:", end_year)

years = np.arange(start_year, end_year + 1, 1)
years = [str(i) for i in years]

'''
The range of years and lat/lon can be specified by the user. Note that the last year of the range is not included.
So, for example, years = np.arange(1992, 2003) would give 1992, 1993, ... 2001, 2002. 2003 would not be included.
'''


def get_suss(meteo, fluxes, susslats, susslons):
    susslats = meteo["lat"].sel(lat = susslats).values
    susslons = meteo["lon"].sel(lon = susslons).values
    times = meteo["time"].values
    precipsuss = meteo["Prec"].sel(lat = susslats, lon = susslons).values
    swesuss = fluxes["SWE"].sel(lat = susslats, lon = susslons).values
    rofsuss = fluxes["Runoff"].sel(lat= susslats, lon = susslons).values
    bassuss = fluxes["Baseflow"].sel(lat= susslats, lon = susslons).values
    etsuss = fluxes["TotalET"].sel(lat= susslats, lon = susslons).values

    sussdata = xr.Dataset({"PRECIP": (("time", "lat", "lon"), precipsuss), "SWE": (("time", "lat", "lon"), swesuss), "ROF": (("time", "lat", "lon"), rofsuss),
                          "ET": (("time", "lat", "lon"), etsuss), "BASE": (("time", "lat", "lon"), bassuss)
                          },
                          {"time": ("time", times), "lat": susslats, "lon": susslons})
    return sussdata

'''
This function creates a dataset of daily precipitation, runoff, and SWE within the specified lat/lon bounds.
The variables are renamed to "PRECIP," "ROF," and "SWE" respectively to be consistent with the other two datasets.
This makes comparative analysis a lot easier.
'''


def get_dswe(data):
    swesuss = data["SWE"]
    susslats = data["lat"].values; susslons = data["lon"].values
    times = data["time"][1::].values
    '''
    "times" starts at the second day because dSWE is a comparative parameter. On the first day of the dataset,
    there's nothing against which to compare the SWE.
    '''
    dswesussraw = [swesuss.isel(time = i+1)- swesuss.isel(time = i) for i in range(len(times))];
    '''
    Note that this function uses "time", NOT "times." i is provided from the length of "times," however, which
    prevents an OBOE.
    '''
    dswedata = xr.Dataset({"dSWE": (("time", "lat", "lon"), dswesussraw)},
                         {"time": ("time", times), "lat": susslats, "lon": susslons})
    combdata = xr.merge([data.sel(time = times), dswedata])
    return combdata

'''
This function adds dSWE to the dataset of precip, runoff, and SWE. Note that this merged dataset drops the first
day of precip, runoff, and SWE data.
'''


months = [str(i).zfill(2) for i in range(1,13)];
ysusslist = []
for year in years:
    print("Getting "+year)
    susslist = []
    for month in months:
        mstring = RAWDIR+"/L15/L15_Meteo_"+year+month+".nc"
        meteo = xr.open_dataset(mstring)
        fstring = RAWDIR+"/L15/L15_Fluxes_"+year+month+".nc"
        fluxes = xr.open_dataset(fstring)
        susslist.append(get_suss(meteo, fluxes, susslats, susslons))
    sussdata = xr.concat(susslist, dim = "time");
    ysusslist.append(sussdata)
yeardata = xr.concat(ysusslist, dim = "time")
yeardata = get_dswe(yeardata);

'''
Because L15 data is monthly, the get_suss function is run every month to combine the precip, runoff, and SWE into
a single dataset containing data from all days in the user-specified time period. Note that the get_dswe function is
not called until all months and years of data have been marged. This is because the get_dSWE function eliminates the
first day of the dataset in its argument. Having the function run on the full merged dataset rather than individual
months prevents the first day of each month from being dropped.
'''

if not os.path.exists(outdir):
    os.mkdirs(outdir)
startyear = years[0]; endyear = years[-1];
yeardata.to_netcdf(outdir+"/L15_"+startyear+"to"+endyear+"_merged.nc")

'''
This saves the dataset in the L15 directory. After the file is saved, this program shouldn't be run again unless
some aspect of the dataset (latitude, longitude, time period) is being changed.
'''


