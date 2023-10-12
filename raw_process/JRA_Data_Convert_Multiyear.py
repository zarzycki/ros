#!/usr/bin/env python
import os
import numpy as np
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
import sys

## Command line args
## Note, sys.arg[0] is the name of the function
print ("Number of arguments: ", len(sys.argv))
print ("The arguments are: " , str(sys.argv))
RAWDIR = sys.argv[1]
outdir= sys.argv[2]

years = np.arange(1985, 2006, 1); years = [str(i) for i in years]
susslats = slice(39.0, 44.0); susslons = slice(360.-80.0,360.-74.0)

#susslats = slice(39.7, 43.1); susslons = slice(281.5, 284.7)
'''
Year range and lat/lon can be modified by the user. Note that the final year in the range is not included.
For example, setting years = range(1992, 2003) would return 1992, 1993, ... 2001, 2002. 2003 would not be included.
Also note that longitude for the JRA dataset is in 0-360 format instead of -180 to 180.
'''


# In[3]:


def get_suss(precipraw, rofraw, sweraw, susslat, susslon):
    trange = precipraw["time"].values; trange = trange[::4]
    '''
    This returns an array of all days in the dataset at time 00Z.
    '''
    precipsuss6h = precipraw.sel(lat = susslat, lon = susslon)
    rofsuss6h = rofraw.sel(lat = susslat, lon = susslon)
    swesuss6h = sweraw.sel(lat = susslat, lon = susslon)
    '''
    This returns 6-hour accumulated precip, mean runoff, and mean SWE for each gridpoint in the specified
    latitude/longitude range (in this example, tne Susquehanna river basin).
    '''
    precipsuss = [8.64*10**7*precipsuss6h.sel(time = slice(i, i+np.timedelta64(1, "D"))).mean(dim = "time") for i in trange]
    precipsuss = xr.concat(precipsuss, dim = "time")
    '''
    This averages 4 6-hour accumulated precipitation fields at 00Z, 06Z, 12Z, and 18Z each day, returning a single
    temporally averaged data array for the basin. The "concat" function puts the data arrays in temporal order.
    However, at this point, the "time" coordinate only reads "0, 1, 2", etc, and isn't yet assigned to specific days.
    The factor of 8.64*10^7 converts from m/s to mm/day.
    '''
    rofsuss = [8.64*10**7*rofsuss6h.sel(time = slice(i, i+np.timedelta64(1, "D"))).mean(dim = "time") for i in trange]
    rofsuss = xr.concat(rofsuss, dim = "time")
    '''
    Same as above for runoff
    '''
    swesuss = [swesuss6h.sel(time = slice(i, i+np.timedelta64(1, "D"))).mean(dim = "time") for i in trange]
    swesuss = xr.concat(swesuss, dim = "time")
    '''
    Same as above for SWE. Note that no conversion factor is needed here, since the units are already in mm.
    (Technically kg/m^2, which works out to the same thing given a water density of 1000kg/m^3)
    '''
    sussdata = xr.merge([precipsuss, rofsuss, swesuss])
    sussdata = sussdata.assign_coords({"time": ("time", trange)})
    '''
    This combines all data arrays into a single dataset, and assigns the time coordinate to the list of 00Z dates
    from above.
    '''
    return sussdata

def get_dswe(sussdata):
    susslats = sussdata["lat"].values; susslons = sussdata["lon"].values
    times = sussdata["time"][1::].values
    '''
    "times" starts at the second entry here because dSWE is a comparative parameter; The first dSWE entry is the
    change in SWE between the first and second days. On the very first day of the dataset, there's nothing against
    which to compare the SWE.
    '''
    dswesuss = [sussdata["SWE"].isel(time = i+1)-sussdata["SWE"].isel(time = i) for i in range(len(times))]
    '''
    This just subtracts the previous day's SWE from the current day's SWE. A negative dSWE indicates a decrease
    in SWE, while a positive dSWE indicates an increase.
    '''
    dswe = xr.Dataset({"dSWE" :(("time", "lat", "lon"), dswesuss)},
                     {"time": ("time", times), "lat": susslats, "lon": susslons})

    combdata = xr.merge([sussdata.sel(time = times), dswe])
    '''
    This adds dSWE to the existing dataset of precip, runoff, and SWE. Note that the times start at the second day
    here as well.
    '''
    return combdata

years = range(1985, 2006, 1); years = [str(i) for i in years]
wlist = []
for year in years:
    print("Getting "+year)
    precipdata = xr.open_dataset(RAWDIR+"/JRA/JRA.h1."+year+".PRECT.nc")
    rofdata = xr.open_dataset(RAWDIR+"/JRA/JRA.h1."+year+".ROF.nc")
    swedata = xr.open_dataset(RAWDIR+"/JRA/JRA.h1."+year+".SWE.nc")
    wdata = get_suss(precipdata, rofdata, swedata, susslats, susslons)
    wdata = wdata.sel(time=~((wdata.time.dt.month == 2) & (wdata.time.dt.day == 29)))
    wlist.append(wdata)
sussdata = xr.concat(wlist, dim = "time")
'''
This creates a list of year-long basin-wide daily averaged datasets as detailed above, which are then concatenated
into a single dataset. The reason for this is that this allows only the very first day of the entire multi-year
dataset to be dropped when computing dSWE, as opposed to dropping the first day from every year if doing
the dSWE calculations on a year-by-year basis.
'''
sussdata = get_dswe(sussdata)
sussdata = sussdata.rename({"PRECT": "PRECIP"})
'''
Each model has its own weird name for the different fields. I chose to rename them to the final datasets
identical in variable names for easy comparison.
'''
#tdata = get_suss(precipdata, rofdata, swedata, susslats, susslons); print(tdata)

if not os.path.exists(outdir):
    os.mkdirs(outdir)
startyear = years[0]; endyear = years[-1]
sussdata.to_netcdf(outdir+"/JRA_"+startyear+"to"+endyear+"_merged.nc")
'''
This saves the final combined dataset, so this program shouldn't need to be run more than once unless the temporal
spacing or basin needs to be changed.
'''
