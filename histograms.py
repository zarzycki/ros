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
basin_shape=str(sys.argv[2]) # What is the basin flag?

print(which_thresh)

## Essentially hardcoded...
outputdir="./output/"+basin_shape+"/"
histdir = outputdir+"/hists/"

csv_file = outputdir+"/csv/supercat.csv"

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

varlist = ['st_swe','wt_rof','pt_pre','Event Length', 'Average dSWE', 'Max dSWE', 'Average Runoff', 'Max Runoff', 'Average Precip', 'Max Precip', 'Average fSWE', 'Max fSWE']
labellist = ['st_swe','wt_rof','pt_pre','Event Length', 'Average dSWE', 'Max dSWE', 'Average ROF', 'Max ROF', 'Average PRECIP', 'Max PRECIP', 'Average fSWE', 'Max fSWE']
xaxislist = ['st_swe','wt_rof','pt_pre','Event Length', 'SWE change', 'SWE change', 'Runoff', 'Runoff', 'Precipitation', 'Precipitation', 'Average fSWE', 'Max fSWE']

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
outdf.to_csv(outputdir+"/csv/table_stats_"+perclabel+".csv")

##### Plotting

### The settings control the figure size
figsize = (6.5, 5)            # Leave as constant to format panels in LaTeX correctly
title_position = [0.5, 0.92]  # If the second number is smaller, title is moved "down" y-axis

###-----> Write out histograms of various statistical variables
NBINS = 8
ytick_step_size = 0.2     # Set step size for even number ticks

ii=0 # Iteration integer for getting labellist
for var in varlist:
    print(var)

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

    # Determine global min/max for x-axis
    global_min = float('inf')
    global_max = float('-inf')
    global_min = min(global_min, x1.min(), x2.min(), x3.min(), x4.min())
    global_max = max(global_max, x1.max(), x2.max(), x3.max(), x4.max())
    if global_min == global_max:
        global_min -= 0.1
        global_max += 0.1
    bin_edges = np.linspace(global_min, global_max, NBINS + 1)

    # Determine global min/max for y-axis
    global_y_min = 0.0
    global_y_max = float('-inf')
    datasets = [x1, x2, x3, x4]
    for dataset in datasets:
        weights = np.ones_like(dataset) / len(dataset)
        hist, _ = np.histogram(dataset, bins=bin_edges, weights=weights)
        global_y_max = max(global_y_max, hist.max())
    if global_y_min == global_y_max:
        global_y_max += 0.1
    global_y_max = global_y_max#+0.05
    print('global_y_max ',global_y_max)

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(4, hspace=0)  # No vertical space between subplots
    axs = gs.subplots(sharex=True)
    datasets = {'L15': x1, 'NLDAS': x2, 'JRA': x3, 'E3SM': x4}
    colors = ['mediumslateblue', 'lightskyblue', 'orange', 'black']

    for ax, (dataset, color, label) in zip(axs, zip(datasets.values(), colors, datasets.keys())):
        weights = np.ones_like(dataset) / len(dataset)
        ax.hist(dataset, histtype='bar', bins=bin_edges, alpha=0.95, weights=weights, color=color, label=label, zorder=10)
        #ax.set_ylabel("PDF (%)")
        ax.legend(loc="upper right")
        ax.set_xlim(global_min, global_max)  # Set consistent x-axis limits
        ax.set_ylim(global_y_min, global_y_max)  # Set consistent x-axis limits

        #print(f"{label} y-axis limits before tick adjustment: {ax.get_ylim()}")

        # Customize y-ticks to add a buffer
        y_ticks = np.arange(global_y_min, global_y_max + ytick_step_size, ytick_step_size)
        y_tick_labels = ['' if i == 0 or i == len(y_ticks) - 1 else f"{tick:.1f}" for i, tick in enumerate(y_ticks)]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_labels)

        #print(f"{label} y-axis limits after tick adjustment: {ax.get_ylim()}")

        # Add light gray grid lines
        ax.grid(axis='y', color='lightgray', linestyle='--', linewidth=0.7, zorder=0)

    # Convert CDF units to percentage (i.e., 0.3 -> 30)
    #formatter = FuncFormatter(to_percentage)
    #plt.gca().yaxis.set_major_formatter(formatter)

    # Set x-axes
    if var == 'Event Length':
        axs[-1].set_xlabel(xaxislist[ii] + " (days)")
    elif var == 'Average fSWE' or var == 'Max fSWE':
        axs[-1].set_xlabel(xaxislist[ii] + " (fraction)")
    else:
        axs[-1].set_xlabel(xaxislist[ii] + " (mm/day)")

    # Add a single y-label to the figure
    fig.text(0.06, 0.5, 'PDF (%)', va='center', ha='center', rotation='vertical')

    plttitle = plt.suptitle(labellist[ii])
    plttitle.set_position(title_position)

    newstr = var.replace(" ", "_")  # replace any spaces with underlines for filenaming
    plt.savefig(histdir + "/" + newstr + "_" + perclabel + ".pdf")
    plt.close()

    ii += 1  # update iter at end of loop for next one

###-----> Write out single histogram

events=outdf['Num']

kwargs = dict(histtype='step', bins=NBINS, alpha=0.75)

x = outdf.index
events=outdf['Num']

x_pos = [i for i, _ in enumerate(x)]

plt.figure(figsize=figsize)

plt.bar(x_pos, events, color=('black','orange','mediumslateblue','lightskyblue'), zorder=10)

plt.xticks(x_pos, x)

plttitle = plt.suptitle("Events")
plttitle.set_position(title_position)

plt.ylabel("Number events", labelpad=5)  # Adjust labelpad to move the y-axis label further away
plt.xlabel("Data Product")

# Get the current axes and plot grid lines
ax = plt.gca()
ax.grid(axis='y', color='lightgray', linestyle='--', linewidth=0.7, zorder=0)

newstr="events"
plt.savefig(histdir+"/"+newstr+"_"+perclabel+".pdf")
plt.close()
