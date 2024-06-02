import numpy as np
import xarray as xr
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from datetime import datetime, timedelta
import os

def is_odd(num):
    return num % 2 != 0

def get_events(data, wthresh, sthresh, pthresh, fthresh, window, model, basin, config):

    # Do we return moving window timeseries or raw daily values?
    # False will accurately capture "real" extrema
    output_smoothed = False

    # Straight average areal
    #dswe = data["dSWE"]; rof = data["ROF"]; precip = data["PRECIP"]

    # Weight area by latitude
    weights = np.cos(np.deg2rad(data["lat"]))
    weights.name = "weights"
    rof = data["ROF"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
    dswe = data["dSWE"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
    precip = data["PRECIP"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)

    #datestrings = dswe["time"].dt.strftime("%Y-%m-%d").values
    dates = dswe["time"]
    '''
    Datestrings takes all dates and puts them in a YYYY-MM-DD format. Dates keeps the original datetime formatting
    Originally, this function used the datestring field to store event days, but I've changed it to datetime for
    easier computation.
    '''

    rosevents = []
    datelist, preciplist, runofflist, dswelist, fswelist = (np.array([]) for i in range(5))
    dtlist = np.array([], dtype = "datetime64")

    # Initialize arrays for smoothed values
    wprecip_smoothed = np.full(len(dates), np.nan)
    wrof_smoothed = np.full(len(dates), np.nan)
    wdswe_smoothed = np.full(len(dates), np.nan)
    wfswe_smoothed = np.full(len(dates), np.nan)
    fswe = np.full(len(dates), np.nan)

    '''
    Initializes several ndarrays for use in computation below.
    '''
    tempdate = 0

    ## Window logic to center smoothing.
    if (is_odd(window)):
        windowst = int(np.ceil(window/2))-1
        print("The window is: "+str(window)+" odd")
    else:
        windowst = int(np.ceil(window/2))
        print("The window is: "+str(window)+" even")
    windowen = int(np.ceil(window/2))
    print("Window front/back: "+str(windowst)+" "+str(windowen))

    for tindex in range(len(dates)):
        # Smoothed values (this days running mean)
        start_smooth_index=max(0,tindex-windowst)
        end_smooth_index=min(tindex+windowen,len(dates))
        #print(str(start_smooth_index),' ',str(end_smooth_index))
        wprecip = precip.isel(time = slice(start_smooth_index, end_smooth_index)).mean()
        wrof = rof.isel(time = slice(start_smooth_index, end_smooth_index)).mean()
        wdswe = -1*dswe.isel(time = slice(start_smooth_index, end_smooth_index)).mean()

        denominator = wprecip + np.maximum(wdswe, 0)
        wfswe = np.where(denominator < 1e-10, 0, np.maximum(wdswe, 0) / denominator)

        # Store smoothed values in arrays
        wprecip_smoothed[tindex] = wprecip
        wrof_smoothed[tindex] = wrof
        wdswe_smoothed[tindex] = wdswe
        wfswe_smoothed[tindex] = wfswe

        # Reset wfse if negative threshold (i.e., no fraction thresholding)
        if fthresh < 0.0:
            wfswe = 0.0

        # Exact values (this days exact daily obs)
        xprecip = precip.isel(time = tindex)
        xrof = rof.isel(time = tindex)
        xdswe = -1*dswe.isel(time = tindex)

        denominator = xprecip + np.maximum(xdswe, 0)
        xfswe = np.where(denominator < 1e-10, 0, np.maximum(xdswe, 0) / denominator)

        fswe[tindex] = xfswe

        # Reset xfswe if needed
        if fthresh < 0.0:
            xfswe = 0.0

        '''
        This looks at three fields separately: The amount of liquid-equivalent precipitation, the amount
        of surface runoff, and the DECREASE in SWE over the specified time period. The user can specify the number
        of days to be averaged. This is done in an attempt to capture the impacts of a multi-day event.

        In this case, the code is taking an areal and time-averaged (over five days) mean of these different
        quantities. The use of a mean rather than a sum ensures that the criteria are the same between model+"/"+models of
        different spatial resolution.
        '''

        ### Debugging print
        #print(str(tindex)+" "+str(dates[tindex].values)+" "+str(wrof.values)+"      "+str(rof[tindex].mean().values))

        if wrof >= wthresh and wdswe >= sthresh and wprecip >= pthresh and wfswe >= fthresh:
            '''
            This checks if a day has a runoff and snowmelt component that exceeds some user-defined criteria.
            This is done to filter out very small events which don't have significant impacts. A half-inch of
            snow melting likely isn't going to do much more than make the ground a little muddy.
            '''
            #tdate = datestrings[tindex]
            tdt = dates[tindex]
            '''
            Once we've determined that a certain 5-day period fits the criteria, we store the first day of the
            period. Note that this is a rolling system. If the 5-day period beginning on the second day also meets the
            criteria, we store the second day as well, and so on.
            '''
            #print(type(tdate))

            if tindex == (tempdate+1) or tempdate == 0:
                '''
                This checks if two days are right next to one another. If they are, they will be added to a sequence
                of days, which will be stored as an "event." This is done to keep particular multiday flooding events
                together.
                '''

                dtlist = np.append(dtlist, tdt)
                if output_smoothed:
                    preciplist = np.append(preciplist, wprecip)
                    runofflist = np.append(runofflist, wrof)
                    dswelist = np.append(dswelist, wdswe)
                    fswelist = np.append(fswelist, wfswe)
                else:
                    preciplist = np.append(preciplist, xprecip)
                    runofflist = np.append(runofflist, xrof)
                    dswelist = np.append(dswelist, xdswe)
                    fswelist = np.append(fswelist, xfswe)

                '''
                This stores the start day, mean precipitation, mean runoff, and mean dSWE across the basin for the
                5-day period.
                '''
            tempdate = tindex
            '''
            This reassigns tempdate to the start date of the 5-day period, regardless of whether or not the period
            meets the criteria. This is done to check if days are consecutive.
            '''
        elif wrof < wthresh or wdswe < sthresh:  # do not include a pthresh here because we can have a long lag of snowmelt/runoff after trigger event (slow-rise)
            # reset tempdate
            tempdate = 0

            if len(dtlist) >=1:
                event = {"Dates": np.copy(dtlist), "Precips": np.copy(preciplist), "Runoffs": np.copy(runofflist), "dSWEs": np.copy(dswelist), "fSWEs": np.copy(fswelist)}
                rosevents.append(event)
                datelist, preciplist, runofflist, dswelist, fswelist = (np.array([]) for i in range(5))
                dtlist = np.array([], dtype = "datetime64")
                '''
                This "stops" the event when it's over, and stores the statistics for the event in a list
                of dictionaries. It then resets the ndarrays for the next event.
                '''

    #for tindex in range(len(dates)):
    #    print(f"precip({tindex}): {precip[tindex].item()}  wprecip({tindex}): {wprecip_smoothed[tindex]}")
    mean_precip = precip.mean().item()
    mean_wprecip = np.nanmean(wprecip_smoothed)  # Use np.nanmean to ignore NaNs in the smoothed array
    print("\nMeans of precip and wprecip:")
    print(f"Mean of precip: {mean_precip}")
    print(f"Mean of wprecip: {mean_wprecip}")

    # Create a new xarray.Dataset to store the data
    dataset = xr.Dataset(
        {
            "precip": (["time"], precip.values),
            "wprecip": (["time"], wprecip_smoothed),
            "dswe": (["time"], dswe.values),
            "wdswe": (["time"], wdswe_smoothed),
            "rof": (["time"], rof.values),
            "wrof": (["time"], wrof_smoothed),
            "fswe": (["time"], fswe),
            "wfswe": (["time"], wfswe_smoothed),
            "wthresh": wthresh,
            "sthresh": sthresh,
            "pthresh": pthresh,
            "fthresh": fthresh,
        },
        coords={
            "time": dates,
        }
    )

    # Save the dataset to a NetCDF file
    outputdir="./output/"+basin+"/tseries/"
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputfile="tseries_"+model+"_"+basin+"_"+config+".nc"
    dataset.to_netcdf(outputdir+"/"+outputfile)

    return rosevents

def get_w_s_perc(data, window):

    ## This returns single long arrays
    # Straight weighting by areal avg.
    #dswe = data["dSWE"]; rof = data["ROF"]; precip = data["PRECIP"]
    # Weight area by latitude
    weights = np.cos(np.deg2rad(data["lat"]))
    weights.name = "weights"
    rof = data["ROF"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
    dswe = data["dSWE"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)
    precip = data["PRECIP"].weighted(weights).mean(dim = ["lat", "lon"], skipna=True)

    dates = dswe["time"]

    pprecip = []
    prof = []
    pdswe = []
    pfswe = []

    tempdate = 0
    for tindex in range(len(dswe["time"])):
        pprecip += [precip.isel(time = slice(tindex, tindex+window)).mean()]
        prof += [rof.isel(time = slice(tindex, tindex+window)).mean()]
        pdswe += [-1*dswe.isel(time = slice(tindex, tindex+window)).mean()]
        pfswe += [ \
            -1*dswe.isel(time = slice(tindex, tindex+window)).mean() / \
            ( -1*dswe.isel(time = slice(tindex, tindex+window)).mean() + \
            precip.isel(time = slice(tindex, tindex+window)).mean() ) \
            ]

    return pprecip, prof, pdswe, pfswe

def get_df(events):
    # This is an attempt to create a single comprehensive dataframe describing the statistics for all events
    # in a certain basin and time period. Each row of the dataframe is an event. The fields are fairly self-explanatory.
    # The "Magnitude" is a little more complicated, and combines the precipitation, runoff, and dSWE for each event. This
    # is used in the bubble plots below, and can also be used to gauge how "severe" an event is. I'm still not sure if
    # precipitation should be included in the magnitude calculation, and that's something I'm working on.
    eventdf = pd.DataFrame({"Event": np.arange(0, len(events), 1),
                            "Event Dates": [event["Dates"] for event in events],
                            "Start Dates": [event["Dates"][0] for event in events],
                            "End Dates": [event["Dates"][-1] for event in events],
                            "Event Length": [len(event["Dates"]) for event in events],
                            "Total Magnitude": [sum(event["Precips"]+event["Runoffs"]+event["dSWEs"]) for event in events],
                            "Peak Magnitude": [max(event["Precips"]+event["Runoffs"]+event["dSWEs"]) for event in events],
                            "Average Magnitude": [sum(event["Precips"]+event["Runoffs"]+event["dSWEs"])/len(event["Precips"]) for event in events],
                            "Total Precip": [sum(event["Precips"]) for event in events],
                            "Max Precip": [max(event["Precips"]) for event in events],
                            "Average Precip": [sum(event["Precips"])/len(event["Precips"]) for event in events],
                            "Total Runoff": [sum(event["Runoffs"]) for event in events],
                            "Max Runoff": [max(event["Runoffs"]) for event in events],
                            "Average Runoff": [sum(event["Runoffs"])/len(event["Runoffs"]) for event in events],
                            "Total dSWE": [sum(event["dSWEs"]) for event in events],
                            "Max dSWE": [max(event["dSWEs"]) for event in events],
                            "Average dSWE": [sum(event["dSWEs"])/len(event["dSWEs"]) for event in events],
                            "Total fSWE": [sum(event["fSWEs"]) for event in events],
                            "Max fSWE": [max(event["fSWEs"]) for event in events],
                            "Average fSWE": [sum(event["fSWEs"])/len(event["fSWEs"]) for event in events]
                            })
    return eventdf

def get_wyear(year, sussdata):
    #For a certain year (ex. 1980), this returns dates from the corresponding water year (1 Oct. 1980 to 30 Sept. 1981).
    #This is done to keep winters together.
    pltdates = sussdata["time"]
    wyear = pltdates.sel(time = slice(year+"-10-01", str(int(year)+1)+"-09-30"))
    return wyear

def get_winter(sussdata):
    pltdates = sussdata["time"]
    month_idxs=pltdates.groupby('time.month').groups
    # Extract the time indices corresponding to all the Januarys
    jan_idxs=month_idxs[1]
    wyear=pltdates.isel(time=jan_idxs)
    return wyear

def get_wyeardict(years, eventdf, sussdata):
    #This creates a dictionary with each water year serving as a key. In each water year is a list of events
    #that occurred in that water year. EAch entry in the list contains the event statistics described above in the
    #"get_df" function.

    #This examines the first winter in the dataset. This first winter may have rain-on-snow events, but
    #would not be otherwise included in the list of water years.
    years.insert(0, str(int(years[0])-1))

    wyeareventsdict = {}
    for year in years:
        wyearevents = []
        wyear = get_wyear(year, sussdata);
        for event in eventdf["Event"]:
            if (np.isin(np.datetime64(eventdf.loc[event].loc["Start Dates"]), wyear).any()):
                wyearevents.append(eventdf.loc[event])
        wyeareventsdict[year] = wyearevents.copy()
    return wyeareventsdict

def get_wyeardates(years, wyeardict):
    #This returns all dates in each water year on which an event occurred. So, for example, if there were three
    #events in water year 1980, the first five days long, the second three days long ,and the third four days long,
    #wyeardates[1980] would have 12 entries.

    wyeardates = {}
    for year in years:
        wyeardates[year] = [date for evdates in wyeardict[year] for date in evdates[1]]
    return wyeardates

def get_streamdata(usgs_station_id,years):

    #streamraw = pd.read_csv("./data/suss_streamflows3.csv")
    streamraw = pd.read_csv("./data/"+usgs_station_id+".txt",delimiter="\t",comment='#')
    #https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=14211720&legacy=&referred_module=sw&period=&begin_date=1985-01-01&end_date=2005-12-31
    #In my case, this is a file I downloaded from https://waterdata.usgs.gov/nwis/dv?referred_module=sw
    #and uploaded to the jupyter server. Make sure that if you're doing this yourself for a different basin
    #or different set of years, you download a file at the location that you're interested in, select
    #the variable "streamflow," select the date range that corresponds to the years you're looking at.

    # Regex to find the column that contains streamflow since the leading integer can change
    streamflow_col = streamraw.filter(regex=r'\d+_00060_00003').columns[0]
    # Rename column to just be "Streamflow"
    streamraw = streamraw.rename(columns = {streamflow_col: "Streamflow"})

    groupdays = streamraw.groupby("datetime").mean(numeric_only=True);
    truedays = [np.datetime64(day) for day in groupdays.index]
    truedays2 = pd.date_range(years[0]+"-01-01",str(int(years[-1]) + 1)+"-12-31");
    #groupdays  = groupdays.reindex(labels = "datetime", index = truedays)
    groupdays.index = truedays

    groupdays2 = pd.DataFrame({"Streamflow": groupdays["Streamflow"]}, index = truedays)
    groupdays3 = groupdays2.reindex(index = truedays2)

    groupdaysw = groupdays3[[day.month <=4 or day.month >=11 for day in groupdays3.index]]
    groupdaysw = groupdaysw.rename_axis("datetime")
    groupdaysw = groupdaysw["Streamflow"]

    return groupdaysw

def get_prank(sarray, svals):

    prs = []

    #This filters out all days with unrecorded streamflow when calculating streamflow percentiles for each event.
    #This is done to avoid misleading percentiles. For example, if any integer value is considered greater than
    #an nan, and there are 20 nans in a 40-element array, then even the lowest value will be considered 50th
    #percentile, which is obviously not useful.
    msarray = sarray[np.logical_not(np.isnan(sarray))]

    # Get percentiles for each day during the event
    prs = [((len(msarray[msarray<sval])+0.5*len(msarray[msarray == sval]))/len(msarray))*100 for sval in svals]

    return prs

def get_evpcts(evdf, streamsuss, swindow):

    #This function returns a list of percentiles given a list of streamflow values. This is used to find the
    #streamflow percentiles for each day (where stream data was recorded) in each event.
    nstartdates = evdf["Start Dates"].size
    emptylist = []
    for xx in range(nstartdates):
      emptylist.append([[]])

    evdf["Streamflow Percentiles"] = emptylist
    evdf["Max Streamflow Percentile"] = emptylist
    evdf["Starting Streamflow Percentile"] = emptylist
    for event in evdf["Event"]:
        sd = evdf["Start Dates"].loc[event]
        # The -1 avoids double-counting the first day. The int() is because this is by default in np.int64 for some reason
        evlen = int(evdf["Event Length"].loc[event]-1);

        streamdays = list(pd.date_range(sd, sd+timedelta(days = evlen+swindow)))

        # CMZ: 8/16/22 --> for now we'll assume we have streamflow data past end of model data
        #if streamdays[-1].year > evdf["Start Dates"].iloc[len(evdf["Start Dates"])-1].year:
        if 0 == 1:
            # If our "window" goes past the end of the dataset, let's just call it a day and add some "nans"
            evdf["Streamflow Percentiles"].loc[event] = -99999.0;
            evdf["Max Streamflow Percentile"].loc[event] = -99999.0;
        else:
            streamvals = streamsuss.reindex(streamdays);
            #streamvals = streamsuss.loc[streamdays];
            pcts = get_prank(streamsuss, streamvals);
            evdf["Streamflow Percentiles"].loc[event] = pcts;
            evdf["Max Streamflow Percentile"].loc[event] = np.max(pcts);

        # Starting streamflow percentile is *always* valid!
        evdf["Starting Streamflow Percentile"].loc[event] = pcts[0];

    return evdf

def get_bubble_axes(xaxis, yaxis):

    if xaxis == "dSWE" and yaxis == "PRECIP":
        xlim = (-65, 20); ylim = (0, 60)
    elif xaxis == "PRECIP" and yaxis == "dSWE":
        xlim = (0, 60); ylim = (-50, 50)
    elif xaxis == "ROF" and yaxis == "PRECIP":
        xlim = (0, 25); ylim = (0, 60)
    elif xaxis == "PRECIP" and yaxis == "ROF":
        xlim = (0, 60); ylim = (0, 25)
    elif xaxis == "ROF" and yaxis == "dSWE":
        xlim = (0, 25); ylim = (-65, 20)
    elif xaxis == "dSWE" and yaxis == "ROF":
        xlim = (-65, 20); ylim = (0, 25)
    return (xlim, ylim)

def get_stream_percentiles(streamsuss):
    allstream_pcts = get_prank(streamsuss, streamsuss);
    streamsuss = streamsuss.to_frame()
    streamsuss['Percentiles'] = allstream_pcts
    streamsuss['P999'] = streamsuss['Percentiles'] > 99.9
    streamsuss['P99'] = streamsuss['Percentiles'] > 99.
    streamsuss['P98'] = streamsuss['Percentiles'] > 98.
    streamsuss['P95'] = streamsuss['Percentiles'] > 95.
    streamsuss['P90'] = streamsuss['Percentiles'] > 90.
    streamsuss['P75'] = streamsuss['Percentiles'] > 75.
    streamsuss['P50'] = streamsuss['Percentiles'] > 50.
    streamsussx = streamsuss.to_xarray()
    return streamsussx

def thresh_based_on_perc(percFilter,sussdata,window):
    ppr, prof, pswe, fswe = get_w_s_perc(sussdata,window)
    wt = np.nanpercentile(prof, percFilter)
    st = np.nanpercentile(pswe, percFilter)
    pt = np.nanpercentile(ppr, percFilter)
    ft = np.nanpercentile(fswe, percFilter)
    return wt, st, pt, ft

def change_offset(sussdata,offset):
    offset = int(offset)
    print("OFFSET: Changing offset by "+str(offset))
    ndates = len(sussdata["time"])
    if (offset == -1):
        sussdata["ROF"].values[0:ndates-1,:,:] = sussdata["ROF"].values[1:ndates:,:]
        sussdata["dSWE"].values[0:ndates-1:,:] = sussdata["dSWE"].values[1:ndates:,:]
        sussdata["PRECIP"].values[0:ndates-1:,:] = sussdata["PRECIP"].values[1:ndates:,:]
        sussdata["ROF"].values[ndates-1:,:] = 0.
        sussdata["dSWE"].values[ndates-1:,:] = 0.
        sussdata["PRECIP"].values[ndates-1:,:] = 0.
    else:
        print("other offsets not supported, check function!")

    return sussdata