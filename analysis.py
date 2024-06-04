#!/usr/bin/env python
import numpy as np
import xarray as xr
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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
usgs_station_id=str(sys.argv[3]) # What is the txt to the gauge string?
basin_shape=str(sys.argv[4]) # What is the basin flag?

## For now defaults
wt = 1.4; st = 1.4; pt = 2.0; ft = -1.0  #wt = ROF threshold, st = SWE threshold, #pt = Precip rate threshold, #ft = dSWE frac thresh
window = 5; swindow = 7       #window = netcdf data smoothing window, swindow = streamflow smoothing window
yaxis = "PRECIP"
xaxis = "dSWE"
STYR=1985
ENYR=2005
plot_streams=True
debug_verbose=False

## Essentially hardcoded...
outputdir="./output/"+basin_shape

############## DO NOT EDIT BELOW THIS LINE

print("Analyzing model: "+model)

years = range(STYR, ENYR+1, 1); years = [str(i) for i in years]; startyear = years[0]; endyear = years[-1]
datafile = "./netcdf/"+model+"_"+startyear+"to"+endyear+"_masked_"+basin_shape+".nc"
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

if percFilter > 0.0:
    perclabel = str(int(percFilter))
else:
    perclabel = "AB"

# If we want to pick a percentile instead of a fixed value, get wt + st percentiles consistent with window
if percFilter > 0.0:
    wttmp, sttmp, pttmp, fttmp = thresh_based_on_perc(percFilter,sussdata,window);
    # Only update wt and st for percentiles, keep pt as either 0 or fixed cutoff
    wt = wttmp
    st = sttmp
    # Don't update fraction either
    #if ft > 0.:
    #    ft = fttmp
print('using rof/wt: ',wt,'   swe/st: ',st,'   precip/pt: ',pt,'   dswefrac/ft: ',ft)

# Get event list and put into pandas list
events = get_events(sussdata, wt, st, pt, ft, window, model, basin_shape, perclabel);

pdevents = []
eventdf = get_df(events)
for event in events:
    #pdates = pd.to_datetime(pd.Series(event["Dates"]))
    #print(pd.Series(event["Dates"]))
    pdates = pd.Series(event["Dates"])
    pdevents.append(pdates.values)

wyeardict = get_wyeardict(years, eventdf, sussdata);
wyeardates = get_wyeardates(years, wyeardict);
streamsuss = get_streamdata(usgs_station_id,years);
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
eventdf['ft_fsw'] = ft

## If output subdirs don't exist, create them.
if not os.path.exists(outputdir):
    os.makedirs(outputdir)
if not os.path.exists(outputdir+'/annual_plots/'):
    os.makedirs(outputdir+'/annual_plots/')
if not os.path.exists(outputdir+'/csv/'):
    os.makedirs(outputdir+'/csv/')

## Write events to CSV
eventdf.to_csv(outputdir+"/csv/Events_"+model+"_"+startyear+"to"+endyear+"_"+perclabel+".csv")

add_panels=False
panel_labels = {'L15': 'a.', 'NLDAS': 'b.', 'JRA': 'c.', 'E3SM': 'd.'}

## Only create shaded plots if using normalized framework. Flip to <= 0.0 for fixed thresholds
if percFilter > 0.0:
    print("PLOTTING!")

    # The max/min values for shading should be defined outside of the loop, since min/max is a slow op and the value doesn't change.
    #minshadingyval=min(dswemean)
    #maxshadingyval=max([max(rofmean),max(precipmean)])
    minshadingyval=-60
    maxshadingyval=62

    sum_swe = np.empty(len(years))
    counter=0

    def plot_streams_data(wyear, streamsussx, ax, markstyle, marksize):
        p90, = ax.plot(wyear, xr.where(streamsussx["P90"].sel(datetime=wyear), 55., -9999.), color="lightcyan", marker=markstyle, ms=marksize, linestyle='None', label='_nolegend_')
        p95, = ax.plot(wyear, xr.where(streamsussx["P95"].sel(datetime=wyear), 55., -9999.), color="lightskyblue", marker=markstyle, ms=marksize, linestyle='None', label='_nolegend_')
        p98, = ax.plot(wyear, xr.where(streamsussx["P98"].sel(datetime=wyear), 55., -9999.), color="royalblue", marker=markstyle, ms=marksize, linestyle='None', label='_nolegend_')
        p99, = ax.plot(wyear, xr.where(streamsussx["P99"].sel(datetime=wyear), 55., -9999.), color="midnightblue", marker=markstyle, ms=marksize, linestyle='None', label='_nolegend_')
        p999, = ax.plot(wyear, xr.where(streamsussx["P999"].sel(datetime=wyear), 55., -9999.), color="black", marker=markstyle, ms=marksize, linestyle='None', label='_nolegend_')
        return [p90, p95, p98, p99, p999]

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

        if plot_streams:
            markstyle = '$\u2223$'
            marksize = 35.0
            bars = plot_streams_data(wyear, streamsussx, ax, markstyle, marksize)

        # Debugging
        #if year == 1995:
        #    for day in wyear.time:
        #        day_str = day.dt.strftime('%Y-%m-%d').item()
        #        precip_value = precipmean.sel(time=day).item()
        #        rof_value = rofmean.sel(time=day).item()
        #        dswe_value = dswemean.sel(time=day).item()
        #        print(f"{day_str} {precip_value} {rof_value} {dswe_value}")

        ax.plot(wyear, precipmean.sel(time = wyear), color = "#009E73", label = "PRECIP", linewidth=2.5, alpha = 1.0)
        ax.plot(wyear, 2.5*rofmean.sel(time = wyear), color = "#E69F00", label = "ROF", linewidth=2.0, alpha = 0.8)
        ax.plot(wyear, dswemean.sel(time = wyear), color = "#CC79A7", label = "dSWE", linewidth=1.75, alpha = 0.6)
        for event in pdevents:
            if (np.isin(event, wyear).all()):
                print("Coloring event") if debug_verbose else None;
                ax.fill_between(event, minshadingyval, maxshadingyval, color = "blue", alpha = 0.15)
        '''
        Highlights the flagged ROS events with a red rectangle
        '''
        main_legend = ax.legend(loc='lower left')

        if plot_streams:
            # Create second legend for the bars
            custom_lines = [
                Line2D([0], [0], color="lightcyan", marker='s', markersize=10, linestyle='None'),
                Line2D([0], [0], color="lightskyblue", marker='s', markersize=10, linestyle='None'),
                Line2D([0], [0], color="royalblue", marker='s', markersize=10, linestyle='None'),
                Line2D([0], [0], color="midnightblue", marker='s', markersize=10, linestyle='None'),
                Line2D([0], [0], color="black", marker='s', markersize=10, linestyle='None')
            ]

            bars_legend = ax.legend(custom_lines, ['90%', '95%', '98%', '99%', '99.9%'], loc='lower right', title=None)
            ax.add_artist(main_legend)

        # Create secondary y-axis for ROF
        ax2 = ax.twinx()
        ax2.set_ylim(minshadingyval / 2.5, maxshadingyval / 2.5)
        ax2.set_ylabel("ROF (mm/day)", fontsize=14)
        ax2.tick_params(axis='both', which='major', labelsize=11)
        ax2.grid(False)  # Hide grid for the secondary y-axis

        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("PRECIP, dSWE (mm/day)", fontsize=14)
        ax.set_title(f"{model} RoS Events ({basin_shape})", fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=11)

        if add_panels:
            panel_label = panel_labels.get(model, 'Unknown Model')
            ax.text(0.02, 0.95, panel_label, transform=ax.transAxes, fontsize=30, fontweight='bold', va='top')

        plt.tight_layout()
        fig.savefig(outputdir+"/annual_plots/"+model+"_"+str(year)+"_events.pdf", bbox_inches='tight')
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
    np.savetxt(outputdir+"/csv/"+model+"_yearly_total_SWE.csv", sum_swe, delimiter=",")

    #### ---> Plots of yearly SWE evolution with shaded events

    # reset max shading value for events
    minshadingyval=-1
    maxshadingyval=201

    for year in years:
        print("Plotting SWE year: "+year) if debug_verbose else None;
        year = int(year)
        wyear = pltdates.sel(time = slice(str(year)+"-11-15", str(year+1)+"-04-30"))
        fig, ax = plt.subplots(1, 1, figsize = (8, 4))
        ax.set_ylim(0, 200)
        ax.margins(x=0)
        ax.xaxis.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha = 0.8)

        ax.plot(wyear, swemean.sel(time = wyear), color = "#CC79A7", label = "SWE", linewidth=3.0, alpha = 0.75)
        for event in pdevents:
            if (np.isin(event, wyear).all()):
                print("Coloring event") if debug_verbose else None;
                ax.fill_between(event, minshadingyval, maxshadingyval, color = "blue", alpha = 0.15)

        ax.legend(fontsize=13)
        ax.set_title(model+" SWE evolution ("+basin_shape+")", fontsize=16)
        ax.set_xlabel("Date", fontsize=15)
        ax.set_ylabel("SWE (mm)", fontsize=15)
        ax.tick_params(axis='both', which='major', labelsize=15)

        if add_panels:
            panel_label = panel_labels.get(model, 'Unknown Model')
            ax.text(0.02, 0.95, panel_label, transform=ax.transAxes, fontsize=30, fontweight='bold', va='top')

        plt.tight_layout()
        fig.savefig(outputdir+"/annual_plots/"+model+"_"+str(year)+"_SWE.pdf", bbox_inches='tight')

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
            ax.set_xlabel(xaxis+" (mm/day)", fontsize=16)
            ax.set_ylabel(yaxis+" (mm/day)", fontsize=16)
            # Need to increment year by 1 because of how water year is defined
            ax.set_title(model+" WY"+ str(int(year)+1)+" ("+basin_shape+")", fontsize=16)
            ax.tick_params(axis='both', which='major', labelsize=16)

            if add_panels:
                panel_label = panel_labels.get(model, 'Unknown Model')
                ax.text(0.02, 0.95, panel_label, transform=ax.transAxes, fontsize=30, fontweight='bold', va='top')

            plt.tight_layout()
            fig.savefig(outputdir+"/annual_plots/"+model+"_"+str(year)+"_scatplot.pdf", bbox_inches='tight')
            plt.close()

print("... DONE!")