#!/usr/bin/env python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os
import sys

# Convert CDF units to percentage (i.e., 0.3 -> 30)
def to_percentage(x, pos):
    return f"{x * 100:.0f}"

which_thresh=sys.argv[1]

print(which_thresh)

csv_file = "./output/supercat.csv"

#which_thresh='-1.0'
#which_thresh='95.0'

## Essentially hardcoded...
outputdir="./output/"
histdir = "./hists/"

# Figure out how to label output
if float(which_thresh) > 0.0:
    perclabel = str(int(float(which_thresh)))
else:
    perclabel = "AB"

print(perclabel)

raw_df = pd.read_csv(csv_file)

## If output subdir doesn't exist, create it.
if not os.path.exists(histdir):
    os.makedirs(histdir)

df = raw_df

sub_df = df[df['Thresh'] == which_thresh]

varlist = ['st_swe','wt_rof','pt_pre','Event Length', 'Average dSWE', 'Max dSWE', 'Average Runoff', 'Max Runoff', 'Average Precip', 'Max Precip']
# Labels that match varlist
labellist = ['st_swe','wt_rof','pt_pre','Event Length', 'Average dSWE', 'Max dSWE', 'Average ROF', 'Max ROF', 'Average PRECIP', 'Max PRECIP']

length_written=False
thresh_written=False

columns = ["L15", "NLDAS","JRA","E3SM"]

outdf = pd.DataFrame()

for var in varlist:

    x1 = sub_df.loc[df['Dataset'] == 'L15'][var].values.astype(float)
    x2 = sub_df.loc[df['Dataset'] == 'NLDAS'][var].values.astype(float)
    x3 = sub_df.loc[df['Dataset'] == 'JRA'][var].values.astype(float)
    x4 = sub_df.loc[df['Dataset'] == 'E3SM'][var].values.astype(float)

    # Num events?
    if not length_written:
        print("num events")
        print(len(x1))
        print(len(x2))
        print(len(x3))
        print(len(x4))
        length_written=True
        tmpdf = pd.DataFrame(data=[len(x1),len(x2),len(x3),len(x4)], index=columns, columns=['Num'])
        outdf = pd.concat([outdf,tmpdf],axis=1)

    print(var)
    if var == 'wt_rof':
        print(x1[0])
        print(x2[0])
        print(x3[0])
        print(x4[0])
    else:
        print(x1.mean())
        print(x2.mean())
        print(x3.mean())
        print(x4.mean())

    #Create tmpdf
    tmpdf = pd.DataFrame(data=[x1.mean(),x2.mean(),x3.mean(),x4.mean()], index=columns, columns=[var])
    outdf = pd.concat([outdf,tmpdf],axis=1)

print(outdf)

## Write stats to CSV
outdf.to_csv(outputdir+"/table_stats_"+perclabel+".csv")

##### Plotting

### The settings control the figure size
figsize = (6.5, 5)            # Leave as constant to format panels in LaTeX correctly
title_position = [0.5, 0.92]  # If the second number is smaller, title is moved "down" y-axis

###-----> Write out histograms of various statistical variables

ii=0 # Iteration integer for getting labellist
for var in varlist:

    print(var)

    NBINS=8

    x1 = sub_df.loc[df['Dataset'] == 'L15'][var].values.astype(float)
    x2 = sub_df.loc[df['Dataset'] == 'NLDAS'][var].values.astype(float)
    x3 = sub_df.loc[df['Dataset'] == 'JRA'][var].values.astype(float)
    x4 = sub_df.loc[df['Dataset'] == 'E3SM'][var].values.astype(float)

    # Clip small negative numbers to zero for plotting.
    if var == 'Max dSWE' or var == 'Average dSWE':
        x1[x1 < 0] = 0
        x2[x2 < 0] = 0
        x3[x3 < 0] = 0
        x4[x4 < 0] = 0

    #kwargs = dict(histtype='stepfilled', alpha=0.3, density=True, bins=6, ec="k", linewidth=2.0)

    kwargs = dict(histtype='step', bins=NBINS, alpha=0.75)

    plt.figure(figsize=figsize)

    weights = np.ones_like(x1) / len(x1)
    plt.hist(x1, **kwargs, weights=weights, linewidth=2.9, color='mediumslateblue', label="L15" )

    weights = np.ones_like(x2) / len(x2)
    plt.hist(x2, **kwargs, weights=weights, linewidth=2.3, color='lightskyblue', label="NLDAS" )

    weights = np.ones_like(x3) / len(x3)
    plt.hist(x3, **kwargs, weights=weights, linewidth=1.7, color='orange', label="JRA" )

    weights = np.ones_like(x4) / len(x4)
    plt.hist(x4, **kwargs, weights=weights, linewidth=1.0, color='black', label="E3SM" )

    plt.legend(loc="upper right")

    plttitle = plt.suptitle(labellist[ii])
    plttitle.set_position(title_position)

    # Convert CDF units to percentage (i.e., 0.3 -> 30)
    formatter = FuncFormatter(to_percentage)
    plt.gca().yaxis.set_major_formatter(formatter)

    plt.ylabel("PDF (%)")
    plt.xlabel("mm/day")

    #plt.show()
    newstr=var.replace(" ", "_")  # replace any spaces with underlines for filenaming
    plt.savefig(histdir+"/"+newstr+"_"+perclabel+".pdf")
    plt.close()

    ii=ii+1   # update iter at end of loop for next one

###-----> Write out single histogram

events=outdf['Num']

kwargs = dict(histtype='step', bins=NBINS, alpha=0.75)

x = outdf.index
events=outdf['Num']

x_pos = [i for i, _ in enumerate(x)]

plt.figure(figsize=figsize)

plt.bar(x_pos, events, color=('black','orange','mediumslateblue','lightskyblue'))

plt.xticks(x_pos, x)

plttitle = plt.suptitle("Events")
plttitle.set_position(title_position)

plt.ylabel("Number events")
plt.xlabel("Data Product")

#plt.show()
newstr="events"
plt.savefig(histdir+"/"+newstr+"_"+perclabel+".pdf")
plt.close()
