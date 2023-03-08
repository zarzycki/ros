#!/usr/bin/env python
import numpy as np
import xarray as xr
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from analysis_helpers import *
import sys
import os

## Command line args
## Note, sys.arg[0] is the name of the function
print ("Number of arguments: ", len(sys.argv))
print ("The arguments are: " , str(sys.argv))
model = sys.argv[1]  #E3SM, JRA, L15, NLDAS
percFilter=float(sys.argv[2])  # -1.  (95.)  ## Do we want to filter on a particular threshold?

## For now defaults
wt = 1.4; st = 1.4; pt = 2.0  #wt = ROF threshold, st = SWE threshold, #pt = Precip rate threshold
window = 5; swindow = 7       #window = netcdf data smoothing window, swindow = streamflow smoothing window
yaxis = "PRECIP"
xaxis = "dSWE"
STYR=1985
ENYR=2005
plot_streams=True
debug_verbose=False

## Essentially hardcoded...
outputdir="./output"

############## DO NOT EDIT BELOW THIS LINE

print("Analyzing model: "+model)

years = range(STYR, ENYR+1, 1); years = [str(i) for i in years]; startyear = years[0]; endyear = years[-1]
datafile = "./netcdf/"+model+"_"+startyear+"to"+endyear+"_masked.nc"
sussdata = xr.open_dataset(datafile)

### E3SM is offset by a day (i.e., Jan 2 reports the average of Jan 1)
if model == "E3SM":
    sussdata = change_offset(sussdata,-1)

# Area-weighted means of the precipitation, runoff, SWE, and dSWE.
weights = np.cos(np.deg2rad(sussdata["lat"]))
weights.name = "weights"
rofmean = sussdata["ROF"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
dswemean = sussdata["dSWE"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
swemean = sussdata["SWE"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
precipmean = sussdata["PRECIP"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)

# Get timeseries of dates from dataset
pltdates = sussdata["time"]

# If we want to pick a percentile instead of a fixed value, get wt + st percentiles consistent with window
if percFilter > 0.0:
    wttmp, sttmp, pttmp = thresh_based_on_perc(percFilter,sussdata,window);
    # Only update wt and st for percentiles, keep pt as either 0 or fixed cutoff
    wt = wttmp
    st = sttmp
print('using rof/wt: ',wt,'   swe/st: ',st,'   precip/pt: ',pt)

# Get event list and put into pandas list
events = get_events(sussdata, wt, st, pt, window);
pdevents = []
eventdf = get_df(events)
for event in events:
    #pdates = pd.to_datetime(pd.Series(event["Dates"]))
    #print(pd.Series(event["Dates"]))
    pdates = pd.Series(event["Dates"])
    pdevents.append(pdates.values)

wyeardict = get_wyeardict(years, eventdf, sussdata);
wyeardates = get_wyeardates(years, wyeardict);
streamsuss = get_streamdata(years);
eventdf = get_evpcts(eventdf, streamsuss, swindow)

# If we need info about streamflow percentiles...
if (plot_streams):
    streamsussx = get_stream_percentiles(streamsuss)

## Comment this line to include all percentiles + dates in each event
eventdf = eventdf.drop(columns=['Streamflow Percentiles', 'Event Dates'])

## These lines add constant columns to the CSV for catting/reference
eventdf['Dataset'] = model
eventdf['Thresh'] = percFilter
eventdf['wt_rof'] = wt
eventdf['st_swe'] = st
eventdf['pt_pre'] = pt

## If output subdir doesn't exist, create it.
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

## Write events to CSV
if percFilter > 0.0:
    perclabel = str(int(percFilter))
else:
    perclabel = "AB"
eventdf.to_csv(outputdir+"/Events_"+model+"_"+startyear+"to"+endyear+"_"+perclabel+".csv")

# The max/min values for shading should be defined outside of the loop, since min/max is a slow op and the value doesn't change.
#minshadingyval=min(dswemean)
#maxshadingyval=max([max(rofmean),max(precipmean)])
minshadingyval=-60
maxshadingyval=62

sum_swe = np.empty(len(years))
counter=0

for year in years:
    print("Plotting year: "+year) if debug_verbose else None;
    year = int(year)
    #wyear = pltdates.sel(time = slice(str(year)+"-10-01", str(year+1)+"-09-30"))
    wyear = pltdates.sel(time = slice(str(year)+"-11-15", str(year+1)+"-04-30"))
    fig, ax = plt.subplots(1, 1, figsize = (8, 4))
    ax.set_ylim(-60, 62)
    ax.margins(x=0)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha = 0.8)
    #debugargs="marker='o', mec='k', ms=0.7"

    if (plot_streams):
        #markstyle='$\u25AE$'
        #markstyle='s'
        markstyle='$\u2223$'
        #markstyle='|'
        marksize=25.0
        ax.plot(wyear, xr.where(streamsussx["P75"].sel(datetime = wyear), 55., -9999.), color = "lightcyan", marker=markstyle, ms=marksize, linestyle = 'None', label='_nolegend_')
        ax.plot(wyear, xr.where(streamsussx["P90"].sel(datetime = wyear), 55., -9999.), color = "lightskyblue", marker=markstyle, ms=marksize, linestyle = 'None', label='_nolegend_')
        ax.plot(wyear, xr.where(streamsussx["P95"].sel(datetime = wyear), 55., -9999.), color = "royalblue", marker=markstyle, ms=marksize, linestyle = 'None', label='_nolegend_')
        ax.plot(wyear, xr.where(streamsussx["P99"].sel(datetime = wyear), 55., -9999.), color = "midnightblue", marker=markstyle, ms=marksize, linestyle = 'None', label='_nolegend_')

    ax.plot(wyear, precipmean.sel(time = wyear), color = "#009E73", label = "Precip", linewidth=2.5, alpha = 1.0)
    ax.plot(wyear, 3.0*rofmean.sel(time = wyear), color = "#E69F00", label = "Runoff", linewidth=2.0, alpha = 0.8)
    ax.plot(wyear, dswemean.sel(time = wyear), color = "#CC79A7", label = "dSWE", linewidth=1.75, alpha = 0.6)
    for event in pdevents:
        if (np.isin(event, wyear).all()):
            print("Coloring event") if debug_verbose else None;
            ax.fill_between(event, minshadingyval, maxshadingyval, color = "blue", alpha = 0.15)
    '''
    Highlights the flagged ROS events with a red rectangle
    '''
    ax.legend()
    ax.set_title(model+"-Analyzed Rain-on_Snow Events")
    fig.savefig(outputdir+"/"+model+"_"+str(year)+"_events.pdf")
    '''
    This creates a time series plot of dSWE, runoff, and precipitation for each water year in the dataset, along
    with a red rectangle highlighting each flagged event. This helps to identify the signatures associated with
    rain-on-snow events.
    '''
    plt.close()

    thisYeardSWE=dswemean.sel(time = wyear)
    sum_swe[counter] = np.sum(thisYeardSWE[thisYeardSWE>0].values)
    counter = counter+1

#print(sum_swe)
np.savetxt(outputdir+"/"+model+"_yearly_total_SWE.csv", sum_swe, delimiter=",")

for year in years:
    print("Plotting SWE year: "+year) if debug_verbose else None;
    year = int(year)
    wyear = pltdates.sel(time = slice(str(year)+"-11-15", str(year+1)+"-04-30"))
    fig, ax = plt.subplots(1, 1, figsize = (8, 4))
    ax.set_ylim(0, 200)
    ax.margins(x=0)
    ax.xaxis.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha = 0.8)

    ax.plot(wyear, swemean.sel(time = wyear), color = "#CC79A7", label = "SWE", linewidth=1.75, alpha = 0.6)
    for event in pdevents:
        if (np.isin(event, wyear).all()):
            print("Coloring event") if debug_verbose else None;
            ax.fill_between(event, minshadingyval, maxshadingyval, color = "blue", alpha = 0.15)

    ax.legend()
    ax.set_title(model+"-Analyzed Rain-on_Snow Events")
    fig.savefig(outputdir+"/"+model+"_"+str(year)+"_SWE.pdf")

    plt.close()

xaxis = xaxis.upper(); yaxis = yaxis.upper()
checkbubblevars = np.array(["PRECIP", "ROF", "DSWE"])
if yaxis == xaxis:
    print("You must plot a different variable for each axis")
    pass
elif np.logical_not(np.isin(xaxis, checkbubblevars) and np.isin(yaxis, checkbubblevars)):
    print("Please enter a valid variable to plot: PRECIP, ROF, or dSWE")
    pass
else:
    if xaxis.upper() == "DSWE":
        xaxis = "dSWE"
        signfilter = 0
    elif yaxis.upper() == "DSWE":
        yaxis = "dSWE"
        signfilter = 1
    else:
        sizevar = "dSWE"
        signfilter = 2
    '''
    Lets users not worry about capitalization when entering plotting variables
    '''
    for year in years:
        print("Bubbling year: "+year+"") if debug_verbose else None;
        wyear = get_wyear(year, sussdata)

        #This lets users put in in only the axis variables and have the size variable be selected automatically
        sizevar = (set({"PRECIP", "ROF", "dSWE"}) - set({xaxis, yaxis})).pop()

        sizecoef=2.6
        totdswes = dswemean.sel(time = wyear); totrofs = rofmean.sel(time = wyear); totprecips = precipmean.sel(time = wyear)
        xvals = sussdata[xaxis].mean(dim = ("lat", "lon")).sel(time = wyear)
        yvals = sussdata[yaxis].mean(dim = ("lat", "lon")).sel(time = wyear)
        sivals = sussdata[sizevar].mean(dim = ("lat", "lon")).sel(time = wyear)
        signvals = [xvals, yvals, sivals][signfilter]
        posx = xvals[signvals>0]; negx = xvals[signvals<0]
        posy = yvals[signvals>0]; negy = yvals[signvals<0]
        possize = (sivals[signvals>0])**sizecoef; negsize = (sivals[signvals<0])**sizecoef
        evdates = wyeardates[year]
        evxvals = xvals.sel(time = evdates); evyvals = yvals.sel(time = evdates); evsivals = sivals.sel(time = evdates)
        evsignvals = signvals.sel(time = evdates)
        posxf = evxvals[evsignvals>0]; negxf = evxvals[evsignvals<0]
        posyf = evyvals[evsignvals>0]; negyf = evyvals[evsignvals<0]
        possizef = (evsivals[evsignvals>0]**sizecoef); negsizef = (evsivals[evsignvals<0])**sizecoef

        fig, ax = plt.subplots(1,1)
        ax.set_axisbelow(True)
        ax.grid(True)
        axlims = get_bubble_axes(xaxis, yaxis)
        ax.axvline(0, color = "black")
        ax.axhline(0, color = "black")
        ax.scatter(posx, posy, s = possize, facecolor = "none", edgecolor = "blue")
        ax.scatter(negx, negy, s = negsize, facecolor = "none", edgecolor = "red")
        ax.scatter(posxf, posyf, s = possizef, facecolor = "blue", edgecolor = "blue")
        ax.scatter(negxf, negyf, s = negsizef, facecolor = "red", edgecolor = "red")
        ax.set_xlim(axlims[0])
        ax.set_ylim(axlims[1])
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)
        fig.suptitle(model+" Water Year "+ str(year))
        fig.savefig(outputdir+"/"+model+"_"+str((year))+"_scatplot.pdf")
        plt.close()

print("... DONE!")