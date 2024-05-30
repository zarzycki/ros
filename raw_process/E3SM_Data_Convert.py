#!/usr/bin/env python
import os
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
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

def get_suss(data, susslats, susslons):
    times = [np.datetime64(time) for time in data["time"].values]
    susslats = data["lat"].sel(lat = susslats).values
    susslons = data["lon"].sel(lon = susslons).values
    precipsuss = 8.64*10**4*data["PRECT"].sel(lat = susslats, lon = susslons).values
    rofsuss = 8.64*10**4*data["QOVER"].sel(lat = susslats, lon = susslons).values
    swesuss = data["H2OSNO"].sel(lat = susslats, lon = susslons).values

    sussdata = xr.Dataset({"PRECIP": (("time", "lat", "lon"), precipsuss), "ROF": (("time", "lat", "lon"), rofsuss), "SWE": (("time", "lat", "lon"), swesuss)},
                         {"time": ("time", times), "lat": susslats, "lon": susslons})
    return sussdata

def get_dswe(data):
    swesuss = data["SWE"]
    susslats = data["lat"].values; susslons = data["lon"].values
    times = data["time"][1::].values
    dswesussraw = [swesuss.isel(time = i+1) - swesuss.isel(time = i) for i in range(len(times))]
    dswedata = xr.Dataset({"dSWE": (("time", "lat", "lon"), dswesussraw)},
                         {"time": ("time", times), "lat": susslats, "lon": susslons})
    combdata = xr.merge([data.sel(time = times), dswedata])
    return combdata

months = [str(i).zfill(2) for i in range(1, 13)]
ysusslist = []
for year in years:
    print("Getting "+year)
    susslist = []
    for month in months:
        rawdata = xr.open_dataset(RAWDIR+"/E3SM/cat.NDG-ne30-ERA5-N58."+year+"-"+month+".nc")
        mdata = get_suss(rawdata, susslats, susslons)
        #print(mdata["PRECIP"])
        susslist.append(mdata)
    sussdata = xr.concat(susslist, dim = "time")
    ysusslist.append(sussdata)
yeardata = xr.concat(ysusslist, dim = "time")
yeardata = get_dswe(yeardata)

if not os.path.exists(outdir):
    os.mkdirs(outdir)
startyear = years[0]; endyear = years[-1]
yeardata.to_netcdf(outdir+"/E3SM_"+startyear+"to"+endyear+"_merged.nc")
