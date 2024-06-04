import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
#from scipy.interpolate import Akima1DInterpolator
import pandas as pd

# USGS_gauge="01570500"   # 01570500 for SRB, 14211720 for Willamette, 11425500 for SacRiver
# BASINSHAPE="srb"        # srb, WillametteBasin, SacRB_USGS1802
# python analysis.py JRA 95 $USGS_gauge $BASINSHAPE

plot_fraction=False
add_smoothing=False

dataset='JRA'
threshold='95.0'
start_date = "1995-12-01"
end_date = "1996-02-15"

true_line_thick=0.8
smooth_line_thick=2.5

true_line_colors=['blue','red','green','orange']
smooth_line_colors=['darkblue','darkred','darkgreen','darkorange']
shading_colors=['lightblue','pink','lightgreen','orange']

colored_alpha=0.8
fill_vert=False

vert_line_thick=1.5
event_alpha=0.15

####################################################################################

# Load the NetCDF file
ncdata = xr.open_dataset("../output/srb/tseries/tseries_JRA_srb_95.nc")

# Extract the time series data for precip, wprecip, rof, wrof, and thresholds
precip = ncdata["precip"]
wprecip = ncdata["wprecip"]
rof = ncdata["rof"]
wrof = ncdata["wrof"]
dswe = ncdata["dswe"]
wdswe = -1*ncdata["wdswe"]
if plot_fraction:
    fswe = ncdata["fswe"]
    wfswe = ncdata["wfswe"]

pthresh = ncdata["pthresh"]
wthresh = ncdata["wthresh"]
sthresh = -1*ncdata["sthresh"]
if plot_fraction:
    fthresh = ncdata["fthresh"]


precip_selected = precip.sel(time=slice(start_date, end_date))
wprecip_selected = wprecip.sel(time=slice(start_date, end_date))
rof_selected = rof.sel(time=slice(start_date, end_date))
wrof_selected = wrof.sel(time=slice(start_date, end_date))
dswe_selected = dswe.sel(time=slice(start_date, end_date))
wdswe_selected = wdswe.sel(time=slice(start_date, end_date))
if plot_fraction:
    fswe_selected = fswe.sel(time=slice(start_date, end_date))
    wfswe_selected = wfswe.sel(time=slice(start_date, end_date))

# Apply Savitzky-Golay filter for smoothing
if add_smoothing:
    window_size = 9  # Choose an odd number for the window size
    poly_order = 2  # Polynomial order for the filter
    precip_smoothed = savgol_filter(precip_selected, window_size, poly_order)
    wprecip_smoothed = savgol_filter(wprecip_selected, window_size, poly_order)
    rof_smoothed = savgol_filter(rof_selected, window_size, poly_order)
    wrof_smoothed = savgol_filter(wrof_selected, window_size, poly_order)
    dswe_smoothed = savgol_filter(dswe_selected, window_size, poly_order)
    wdswe_smoothed = savgol_filter(wdswe_selected, window_size, poly_order)
    if plot_fraction:
        fdswe_smoothed = savgol_filter(fdswe_selected, window_size, poly_order)
else:
    precip_smoothed = precip_selected
    wprecip_smoothed = wprecip_selected
    rof_smoothed = rof_selected
    wrof_smoothed = wrof_selected
    dswe_smoothed = dswe_selected
    wdswe_smoothed = wdswe_selected
    if plot_fraction:
        fswe_smoothed = fswe_selected
        wfswe_smoothed = wfswe_selected

# Load the CSV file
events_df = pd.read_csv('../output/srb/csv/supercat.csv')
filtered_events = events_df[(events_df['Dataset'] == dataset) & (events_df['Thresh'] == threshold)]
filtered_events['Start Dates'] = pd.to_datetime(filtered_events['Start Dates'])
filtered_events['End Dates'] = pd.to_datetime(filtered_events['End Dates'])
filtered_events = filtered_events[(filtered_events['Start Dates'] >= start_date) & (filtered_events['End Dates'] <= end_date)]
print(filtered_events['Start Dates'])
print(filtered_events['End Dates'])

# Create subplots
npanels = 3
if plot_fraction:
    npanels = npanels+1

fig, axs = plt.subplots(npanels, 1, figsize=(12, 7), gridspec_kw={'hspace': 0})

# Plot rof and wrof on the second subplot
axs[0].plot(rof_selected.time, rof_smoothed, label='ROF', color=true_line_colors[0], linewidth=true_line_thick)
axs[0].plot(wrof_selected.time, wrof_smoothed, label='ROF$_{sm}$', color=smooth_line_colors[0], linewidth=smooth_line_thick)
axs[0].axhline(y=wthresh, color='grey', linestyle='--', label=f'$t_{{ROF}}$ = {wthresh:.1f}')
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Runoff')
axs[0].legend()
axs[0].set_xticks([])
axs[0].set_ylim([-1,17])

if fill_vert:
    fill_between_min=axs[0].get_ylim()[0]
    fill_between_max=axs[0].get_ylim()[0]
else:
    fill_between_min=wrof_smoothed
    fill_between_max=wthresh

axs[0].fill_between(
    wrof_selected.time,
    fill_between_min,
    fill_between_max,
    where=(wrof_selected >= wthresh),
    facecolor=shading_colors[0],
    alpha=colored_alpha,
)

# Plot dswe and wdswe on the second subplot
axs[1].plot(dswe_selected.time, dswe_smoothed, label='dSWE', color=true_line_colors[1], linewidth=true_line_thick)
axs[1].plot(wdswe_selected.time, wdswe_smoothed, label='dSWE$_{sm}$', color=smooth_line_colors[1], linewidth=smooth_line_thick)
axs[1].axhline(y=sthresh, color='grey', linestyle='--', label=f'$t_{{dSWE}}$ = {sthresh:.1f}')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('dSWE')
axs[1].legend()
axs[1].set_xticks([])
axs[1].set_ylim([-42,22])

# Shading
if fill_vert:
    fill_between_min=axs[1].get_ylim()[0]
    fill_between_max=axs[1].get_ylim()[1]
else:
    fill_between_min=wdswe_smoothed
    fill_between_max=sthresh

axs[1].fill_between(
    wdswe_selected.time,
    fill_between_min,
    fill_between_max,
    where=(wdswe_selected <= sthresh),
    facecolor=shading_colors[1],
    alpha=colored_alpha,
)

# Plot precip and wprecip on the first subplot
axs[2].plot(precip_selected.time, precip_smoothed, label='PRECIP', color=true_line_colors[2], linewidth=true_line_thick)
axs[2].plot(wprecip_selected.time, wprecip_smoothed, label='PRECIP$_{sm}$', color=smooth_line_colors[2], linewidth=smooth_line_thick)
#x1_new = np.linspace(0, len(precip_selected, 5000)
#akima1 = Akima1DInterpolator(precip_selected.time, precip_smoothed)
#axs[2].plot(x1_new, akima1(x1_new), label='precip', color='brown')
axs[2].axhline(y=pthresh, color='grey', linestyle='--', label=f'$t_{{PRECIP}}$ = {pthresh:.1f}')
axs[2].set_ylabel('Precipitation')
axs[2].legend()
axs[2].set_ylim([-1,22])
if plot_fraction:
    axs[2].set_xticks([])

# Shade the background when wprecip is greater than pthresh
# axs[2].fill_between(
#     wprecip_selected.time,
#     wprecip_selected,
#     pthresh,
#     where=(wprecip_selected > pthresh),
#     facecolor='lightgreen',
#     alpha=0.5,
# )

if fill_vert:
    fill_between_min=axs[2].get_ylim()[2]
    fill_between_max=axs[2].get_ylim()[1]
else:
    fill_between_min=wprecip_smoothed
    fill_between_max=pthresh

axs[2].fill_between(
    wprecip_selected.time,
    fill_between_min,
    fill_between_max,
    where=(wprecip_selected >= pthresh),
    facecolor=shading_colors[2],
    alpha=colored_alpha,
)


if plot_fraction:
    axs[3].plot(fswe_selected.time, fswe_smoothed, label='fSWE', color=true_line_colors[3], linewidth=true_line_thick)
    axs[3].plot(wfswe_selected.time, wfswe_smoothed, label='fSWE$_{sm}$', color=smooth_line_colors[3], linewidth=smooth_line_thick)
    axs[3].axhline(y=fthresh, color='grey', linestyle='--', label=f'$t_{{fSWE}}$ = {fthresh:.3f}')
    axs[3].set_xlabel('Date')
    axs[3].set_ylabel('fSWE')
    axs[3].legend()

    # Shading
    if fill_vert:
        fill_between_min=axs[3].get_ylim()[0]
        fill_between_max=axs[3].get_ylim()[1]
    else:
        fill_between_min=wfswe_smoothed
        fill_between_max=fthresh

    axs[3].fill_between(
        wfswe_selected.time,
        fill_between_min,
        fill_between_max,
        where=(wfswe_selected >= fthresh),
        facecolor=shading_colors[3],
        alpha=colored_alpha,
    )

# Add vertical lines for the events
for _, row in filtered_events.iterrows():
    start_date_event = pd.to_datetime(row['Start Dates'])
    end_date_event = pd.to_datetime(row['End Dates'])

    for ax in axs:
        ax.axvline(x=start_date_event, color='black', linestyle='-', linewidth=vert_line_thick)
        ax.axvline(x=end_date_event, color='black', linestyle='-', linewidth=vert_line_thick)
        ax.axvspan(start_date_event, end_date_event, color='grey', alpha=event_alpha)

# Set x-axis limits to start_date and end_date
for ax in axs:
    ax.set_xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))

# Adjust the layout to remove white space between the subplots
plt.tight_layout()
plt.subplots_adjust(hspace=0)

filename = "tseries.pdf"
plt.savefig(filename, bbox_inches='tight')