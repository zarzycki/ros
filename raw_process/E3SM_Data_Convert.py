#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
#get_ipython().run_line_magic('matplotlib', 'notebook')
import matplotlib.pyplot as plt


# In[2]:


years = np.arange(1985, 2006, 1); years = [str(i) for i in years]
#susslats = slice(39.7, 43.1); susslons = slice(-78.5, -75.3)
susslats = slice(39.0, 44.0); susslons = slice(-80.0, -74.0)

# In[3]:


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


# In[4]:


def get_dswe(data):
    swesuss = data["SWE"]
    susslats = data["lat"].values; susslons = data["lon"].values
    times = data["time"][1::].values
    dswesussraw = [swesuss.isel(time = i+1) - swesuss.isel(time = i) for i in range(len(times))]
    dswedata = xr.Dataset({"dSWE": (("time", "lat", "lon"), dswesussraw)},
                         {"time": ("time", times), "lat": susslats, "lon": susslons})
    combdata = xr.merge([data.sel(time = times), dswedata])
    return combdata


# In[5]:


months = [str(i).zfill(2) for i in range(1, 13)]
ysusslist = []
for year in years:
    print("Getting "+year)
    susslist = []
    for month in months:
        rawdata = xr.open_dataset("/storage/home/cmz5202/group/ros/E3SM/cat.NDG-ne30-ERA5-N58."+year+"-"+month+".nc")
        mdata = get_suss(rawdata, susslats, susslons)
        #print(mdata["PRECIP"])
        susslist.append(mdata)
    sussdata = xr.concat(susslist, dim = "time")
    ysusslist.append(sussdata)
yeardata = xr.concat(ysusslist, dim = "time")
yeardata = get_dswe(yeardata)

outdir = "/storage/home/cmz5202/group/ros/proc/"
if not os.path.exists(outdir):
    os.mkdirs(outdir)
startyear = years[0]; endyear = years[-1]
yeardata.to_netcdf(outdir+"/E3SM_"+startyear+"to"+endyear+"_merged.nc")


# In[ ]:




