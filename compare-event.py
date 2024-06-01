import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import xarray as xr
import metpy.calc as mpcalc
import matplotlib.ticker as ticker
import sys
import os

basin_shape=str(sys.argv[1]) # What is the basin flag?
OUTDIR="./output/"+basin_shape+"/"

if basin_shape == 'srb':
    lon_station=-76.8515
    lat_station=40.2171
    event_string='1996-event-srb'
    L15_location='40.28125_-76.90625'
    start_date_str="1996-01-17"
    end_date_str="1996-01-21"
    obs_station="CXY"
    interpolate_obs_T=True
elif basin_shape == 'WillametteBasin':
    lon_station=-123.024444
    lat_station=44.923056
    event_string='1996-event-oregon'
    L15_location='44.90625_-123.03125'
    start_date_str="1996-02-03"
    end_date_str="1996-02-10"
    obs_station="SLE"
    interpolate_obs_T=True
elif basin_shape == 'SacRB_USGS1802':
    lon_station=-121.626111
    lat_station=39.134722
    event_string='1997-event-cali'
    L15_location='39.71875_-121.84375'
    start_date_str="1996-12-30"
    end_date_str="1997-01-06"
    obs_station="MYV"
    interpolate_obs_T=True
else:
    print("invalid basin")
    quit()

if not os.path.exists(OUTDIR+'/event-level/'):
    os.makedirs(OUTDIR+'/event-level/')

############ Automagically get bounds to get nc data

# Convert string to datetime.date
start_date_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
end_date_dt = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

# Calculate the dates for data, one day before and one day after
start_date_data_dt = start_date_dt - datetime.timedelta(days=1)
end_date_data_dt = end_date_dt + datetime.timedelta(days=1)

# Convert dates back to strings
start_date_data = start_date_data_dt.strftime('%Y-%m-%d')
end_date_data = end_date_data_dt.strftime('%Y-%m-%d')

print("Start Date for User:", start_date_str)
print("End Date for User:", end_date_str)
print("Data Start Date:", start_date_data)
print("Data End Date:", end_date_data)

############

### Load obs data
obs = pd.read_csv('./netcdf/event-data/'+event_string+'/obs/'+obs_station+'.csv')
obstime = pd.to_datetime(obs['valid'], format='%Y-%m-%d %H:%M')

obs['tmpf'] = pd.to_numeric(obs['tmpf'], errors='coerce')
obsT = ((obs['tmpf'] - 32.) * 5/9) + 273.15
if interpolate_obs_T :
    obsT = obsT.interpolate()

### L15-VIC data (3-hourly ASCII)
df2 = pd.read_csv('./netcdf/event-data/'+event_string+'/L15/VIC_subdaily_fluxes_Livneh_CONUSExt_v.1.2_2013_'+L15_location,header=None,delimiter='\t')

data = df2.to_numpy()

# Generate a datetime array
masterdatetime=[]
for index, _ in np.ndenumerate(data[:,0]):
    thisdate = datetime.datetime(int(data[index[0],0]), int(data[index[0],1]), int(data[index[0],2]), int(data[index[0],3]))
    masterdatetime.append(thisdate)

# Find indices in masterdatetime where the dates match the start and end dates
stix = np.where(np.array(masterdatetime) == datetime.datetime.strptime(start_date_data, '%Y-%m-%d'))
enix = np.where(np.array(masterdatetime) == datetime.datetime.strptime(end_date_data, '%Y-%m-%d'))
stix = stix[0][0]
enix = enix[0][0]

# Extract relevant variables
L15time = masterdatetime[stix:enix]
L15T = data[stix:enix,5]
L15PREC = data[stix:enix,4]
L15RH = data[stix:enix,7]
L15RH = np.where(L15RH > 100, 100, L15RH)
L15SNOW = np.where(L15T > 273.15, 0, L15PREC)
L15RAIN = np.where(L15T <= 273.15, 0, L15PREC)
L15SNOW = L15SNOW * 3600
L15RAIN = L15RAIN * 3600

# CMZ, appears L15 is in local time, want UTC
for i in range(len(L15time)):
    L15time[i] = L15time[i] + datetime.timedelta(hours=5)

### JRA data

da = xr.open_dataset('./netcdf/event-data/'+event_string+'/JRA/JRA.h1.T2M.nc')
db = xr.open_dataset('./netcdf/event-data/'+event_string+'/JRA/JRA.h1.PRECT.nc')
dc = xr.open_dataset('./netcdf/event-data/'+event_string+'/JRA/JRA.h1.PRECSN.nc')
dd = xr.open_dataset('./netcdf/event-data/'+event_string+'/JRA/JRA.h1.RHREFHT.nc')

da2 = da.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
da2 = da2.sel(time=slice(start_date_data, end_date_data))
db2 = db.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
db2 = db2.sel(time=slice(start_date_data, end_date_data))
dc2 = dc.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
dc2 = dc2.sel(time=slice(start_date_data, end_date_data))
dd2 = dd.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
dd2 = dd2.sel(time=slice(start_date_data, end_date_data))

# Using 2M predictor
jraT = da2.T2M
jraPRECT = db2.PRECT
jraRHREFHT = dd2.RHREFHT
jraRHREFHT = np.where(jraRHREFHT > 100, 100, jraRHREFHT)
jraSNOW = np.where(jraT > 273.15, 0, jraPRECT)
jraRAIN = np.where(jraT <= 273.15, 0, jraPRECT)

# Native
#jraSNOW = dc2.PRECSN
#jraRAIN = jraPRECT
#jraRAIN = jraRAIN - jraSNOW

jratime = da2.time

# Convert from m/s to mm/h
jraRAIN = jraRAIN * 1000 * 3600
jraSNOW = jraSNOW * 1000 * 3600


### E3SM

ea = xr.open_dataset('./netcdf/event-data/'+event_string+'/E3SM/E3SM-catted-native_regrid.v2.nc')
ea2 = ea.sel(lat=lat_station,lon=lon_station,method='nearest')
ea2 = ea2.sel(time=slice(start_date_data, end_date_data))
ea2 = ea2.convert_calendar("standard")

e3smT = ea2.TREFHT
e3smRH = ea2.RHREFHT
e3smRH = np.where(e3smRH > 100, 100, e3smRH)
e3smPRECT = ea2.PRECT
e3smSNOW = np.where(e3smT > 273.15, 0, e3smPRECT)
e3smRAIN = np.where(e3smT <= 273.15, 0, e3smPRECT)
e3smtime = ea2.time

# Convert from m/s to mm/h
e3smRAIN = e3smRAIN * 1000 * 3600
e3smSNOW = e3smSNOW * 1000 * 3600


### NLDAS data
fa = xr.open_dataset('./netcdf/event-data/'+event_string+'/NLDAS/NLDAS-VIC4.0.5.v2.nc')
fa2 = fa.sel(lat=lat_station,lon=lon_station,method='nearest')
fa2 = fa2.sel(time=slice(start_date_data, end_date_data))

NLDAST = fa2.Tair
NLDASPRECT = fa2.Rainf
NLDASQ = fa2.Qair
NLDASP = fa2.PSurf
NLDASSNOW = np.where(NLDAST > 273.15, 0, NLDASPRECT)
NLDASRAIN = np.where(NLDAST <= 273.15, 0, NLDASPRECT)
NLDAStime = fa2.time

# No need to convert since data is kg/m2 over 1 hour = mm/hr
NLDASRAIN = NLDASRAIN
NLDASSNOW = NLDASSNOW

# Convert specific humidity to relative humidity using the formula
#NLDASRH = specific_humidity_to_relative_humidity(NLDASQ, NLDASP, NLDAST)

NLDASRH = mpcalc.relative_humidity_from_specific_humidity(NLDASP,NLDAST,NLDASQ)
NLDASRH = NLDASRH * 100.
NLDASRH = np.where(NLDASRH > 100, 100, NLDASRH)

# Create simple timeseries plot

fig, ax = plt.subplots()

ax.plot(L15time, L15T, 'c', label='L15') # plotting t, a separately
ax.plot(jratime, jraT, 'm', label='JRA') # plotting t, a separately
ax.plot(e3smtime, e3smT, 'y', label='E3SM') # plotting t, a separately
ax.plot(NLDAStime, NLDAST, 'b', label='NLDAS') # plotting t, a separately
ax.plot(obstime, obsT, 'k', label='Obs') # plotting t, a separately
ax.axhline(y=273.15, color='k')

ax.legend()

ax.set(ylim=(258,292))

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H''Z'))
ax.tick_params(axis='x', labelrotation=90)

ax.set_axisbelow(True)
ax.yaxis.grid(color='lightgray', linestyle='dashed')
ax.xaxis.grid(color='lightgray', linestyle='dashed')

left = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
right = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
plt.gca().set_xbound(left, right)

plt.savefig(OUTDIR+"/event-level/timeseries_T_event.pdf", format="pdf", bbox_inches="tight")



# Create figure for manuscript

fig, axs = plt.subplots(2, 2)

# Reference width of bars (based on hourly lines)
refer_width = 0.042

# Settings
snow_color='skyblue'
rain_color='green'
temp_color='red'
rh_color='slateblue'
obs_line_color='goldenrod'

ref_line_color='k'
bot_t_range=250
top_t_range=290

obs_line_width=1.0
freezing_temp=273.15

rain_tick_length = 4

rh_tick_spacing = 25.  # Set the desired tick spacing
rh_tick_length = 3  # Set the desired tick length in points
t_tick_spacing = 10.
t_tick_length = 6

rh_max_axis = 100
rh_line_width=0.9
rh_linestyle='--'

axs[0, 0].bar(L15time, L15SNOW, refer_width*3, label='L15_SNOW', color=snow_color) # plotting t, a separately
axs[0, 0].bar(L15time, L15RAIN, refer_width*3, label='L15_RAIN', color=rain_color) # plotting t, b separately
axs[0, 0].set_title('L15')
ax00 = axs[0, 0].twinx()
ax00.plot(L15time, L15T, temp_color, label='L15') # plotting t, a separately
ax00.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax00.axhline(y=freezing_temp, color=ref_line_color)
ax00.set(ylim=(bot_t_range,top_t_range))
ax00.label_outer()
ax00.tick_params(axis='y', colors=temp_color, length=t_tick_length)  # For y-axis ticks

ax00_2 = axs[0, 0].twinx()
ax00_2.plot(L15time, L15RH, color=rh_color, linestyle=rh_linestyle, linewidth=rh_line_width, label='L15_RH')
ax00_2.set(ylim=(0, rh_max_axis))
ax00_2.label_outer()
ax00_2.tick_params(axis='y', colors=rh_color, length=rh_tick_length)  # For y-axis ticks
ax00_2.set_yticks(np.arange(0, 101, 20))






axs[1, 0].bar(jratime, jraSNOW, refer_width*6, label='JRA_SNOW', color=snow_color) # plotting t, a separately
axs[1, 0].bar(jratime, jraRAIN, refer_width*6, label='JRA_RAIN', color=rain_color) # plotting t, b separately
axs[1, 0].set_title('JRA')
ax10 = axs[1, 0].twinx()
ax10.plot(jratime, jraT, temp_color, label='JRA') # plotting t, a separately
ax10.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax10.axhline(y=freezing_temp, color=ref_line_color)
ax10.set(ylim=(bot_t_range,top_t_range))
ax10.label_outer()
ax10.tick_params(axis='y', colors=temp_color, length=t_tick_length)  # For y-axis ticks

ax10_2 = axs[1, 0].twinx()
ax10_2.plot(jratime, jraRHREFHT, color=rh_color, linestyle=rh_linestyle, linewidth=rh_line_width, label='JRA_RH')
ax10_2.set(ylim=(0, rh_max_axis))
ax10_2.label_outer()
ax10_2.tick_params(axis='y', colors=rh_color, length=rh_tick_length)  # For y-axis ticks
ax10_2.set_yticks(np.arange(0, 101, 20))





axs[0, 1].bar(NLDAStime, NLDASSNOW, refer_width*1, label='NLDAS_SNOW', color=snow_color) # plotting t, a separately
axs[0, 1].bar(NLDAStime, NLDASRAIN, refer_width*1, label='NLDAS_RAIN', color=rain_color) # plotting t, b separately
axs[0, 1].set_title('NLDAS')
ax01 = axs[0, 1].twinx()
ax01.plot(NLDAStime, NLDAST, temp_color, label='NLDAS') # plotting t, a separately
ax01.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax01.axhline(y=freezing_temp, color=ref_line_color)
ax01.set(ylim=(bot_t_range,top_t_range))
ax01.label_outer()
ax01.tick_params(axis='y', colors=temp_color, length=t_tick_length)  # For y-axis ticks

ax01_2 = axs[0, 1].twinx()
ax01_2.plot(NLDAStime, NLDASRH, color=rh_color, linestyle=rh_linestyle, linewidth=rh_line_width, label='NLDAS_RH')
ax01_2.set(ylim=(0, rh_max_axis))
ax01_2.label_outer()
ax01_2.tick_params(axis='y', colors=rh_color, length=rh_tick_length)  # For y-axis ticks
ax01_2.set_yticks(np.arange(0, 101, 20))






axs[1, 1].bar(e3smtime, e3smSNOW, (refer_width*3.), label='E3SM_SNOW', color=snow_color) # plotting t, a separately
axs[1, 1].bar(e3smtime, e3smRAIN, (refer_width*3.), label='E3SM_RAIN', color=rain_color) # plotting t, b separately
axs[1, 1].set_title('E3SM')
ax11 = axs[1, 1].twinx()
ax11.plot(e3smtime, e3smT, temp_color, label='E3SM') # plotting t, a separately
ax11.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax11.axhline(y=freezing_temp, color=ref_line_color)
ax11.set(ylim=(bot_t_range,top_t_range))
ax11.label_outer()
ax11.tick_params(axis='y', colors=temp_color, length=t_tick_length)  # For y-axis ticks

# E3SM panel
ax11_2 = axs[1, 1].twinx()
ax11_2.plot(e3smtime, e3smRH, color=rh_color, linestyle=rh_linestyle, linewidth=rh_line_width, label='E3SM_RH')
ax11_2.set_ylabel('Relative Humidity (%)', color=rh_color)
#ax11_2.tick_params(axis='y', labelcolor=rh_color)
ax11_2.set(ylim=(0, rh_max_axis))
ax11_2.label_outer()
ax11_2.tick_params(axis='y', colors=rh_color, length=rh_tick_length)  # For y-axis ticks
ax11_2.set_yticks(np.arange(0, 101, 20))




# Do things that apply to all subplots
for ax in axs.flat:
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='lightgray', linestyle='dashed')
    ax.xaxis.grid(color='lightgray', linestyle='dashed')
    ax.set(ylim=(0,4.2))
    ax.set(xlim=(start_date_dt,end_date_dt))
    ax.tick_params(axis='x', labelrotation=90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H''Z'))

for ax in axs.flat:
    ax.set_xlabel('Date (UTC)')
    ax.set_ylabel('Precip. rate (mm/hr)', color=rain_color)
    ax.tick_params(axis='y', colors=rain_color, length=rain_tick_length)  # For y-axis ticks

for ax in axs.flat:
    ax.label_outer()

## Label rightmost axes
ax01.set_ylabel('Sfc. temp. (K)',color=temp_color)
ax11.set_ylabel('Sfc. temp. (K)',color=temp_color)
ax01_2.set_ylabel('Relative Humidity (%)', color=rh_color)
ax11_2.set_ylabel('Relative Humidity (%)', color=rh_color)

## Move RH axis to the right
shift_dist=1.29
ax01_2.spines["right"].set_position(("axes", shift_dist))
ax01_2.spines["right"].set_visible(True)
ax11_2.spines["right"].set_position(("axes", shift_dist))
ax11_2.spines["right"].set_visible(True)

plt.savefig(OUTDIR+"/event-level/precip_vs_t.pdf", format="pdf", bbox_inches="tight")

