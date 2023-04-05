import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import numpy as np
import xarray as xr

# Location of station?
lon_station=-76.8515
lat_station=40.2171

### Load obs data
obs = pd.read_csv('./netcdf/1996-event/obs/CXY.csv')
obstime = pd.to_datetime(obs['valid'])
obsT = ((obs['tmpf'] - 32.) * 5/9) + 273.15

### L15-VIC data (3-hourly ASCII)
df2 = pd.read_csv('./netcdf/1996-event/L15/VIC_subdaily_fluxes_Livneh_CONUSExt_v.1.2_2013_40.28125_-76.90625',header=None,delimiter='\t')

data = df2.to_numpy()

# Generate a datetime array
masterdatetime=[]
for index, value in np.ndenumerate(data[:,0]):
    thisdate = datetime.datetime(int(data[index,0]), int(data[index,1]), int(data[index,2]), int(data[index,3]))
    masterdatetime.append(thisdate)

# Find start and end indices
stix = np.where(masterdatetime == np.datetime64(datetime.datetime(1996, 1, 1)))
enix = np.where(masterdatetime == np.datetime64(datetime.datetime(1996, 1, 30)))
stix = stix[0][0]
enix = enix[0][0]

# Extract relevant variables
L15time = masterdatetime[stix:enix]
L15T = data[stix:enix,5]
L15PREC = data[stix:enix,4]
L15SNOW = np.where(L15T > 273.15, 0, L15PREC)
L15RAIN = np.where(L15T <= 273.15, 0, L15PREC)
L15SNOW = L15SNOW * 3600
L15RAIN = L15RAIN * 3600

# CMZ, appears L15 is in local time, want UTC
for i in range(len(L15time)):
    L15time[i] = L15time[i] + datetime.timedelta(hours=5)

### JRA data

da = xr.open_dataset('./netcdf/1996-event/JRA/JRA.h1.1996.T2M.nc')
db = xr.open_dataset('./netcdf/1996-event/JRA/JRA.h1.1996.PRECT.nc')
dc = xr.open_dataset('./netcdf/1996-event/JRA/JRA.h1.1996.PRECSN.nc')

da2 = da.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
da2 = da2.sel(time=slice("1996-01-01", "1996-01-30"))
db2 = db.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
db2 = db2.sel(time=slice("1996-01-01", "1996-01-30"))
dc2 = dc.sel(lat=lat_station,lon=(360.0 + lon_station),method='nearest')
dc2 = dc2.sel(time=slice("1996-01-01", "1996-01-30"))

# Using 2M predictor
jraT = da2.T2M
jraPRECT = db2.PRECT
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

ea = xr.open_dataset('./netcdf/1996-event/E3SM/E3SM-catted-native.nc_regrid.nc')
ea2 = ea.sel(lat=lat_station,lon=lon_station,method='nearest')
ea2 = ea2.sel(time=slice("1996-01-01", "1996-01-30"))
ea2 = ea2.convert_calendar("standard")

e3smT = ea2.TREFHT
e3smPRECT = ea2.PRECT
e3smSNOW = np.where(e3smT > 273.15, 0, e3smPRECT)
e3smRAIN = np.where(e3smT <= 273.15, 0, e3smPRECT)
e3smtime = ea2.time

# Convert from m/s to mm/h
e3smRAIN = e3smRAIN * 1000 * 3600
e3smSNOW = e3smSNOW * 1000 * 3600


### NLDAS data
fa = xr.open_dataset('./netcdf/1996-event/NLDAS/NLDAS-VIC4.0.5.nc')
fa2 = fa.sel(lat_110=lat_station,lon_110=lon_station,method='nearest')
fa2 = fa2.sel(time=slice("1996-01-01", "1996-01-30"))

NLDAST = fa2.TMP_110_HTGL
NLDASPRECT = fa2.NARR_A_PCP_110_SFC_acc1h
NLDASSNOW = np.where(NLDAST > 273.15, 0, NLDASPRECT)
NLDASRAIN = np.where(NLDAST <= 273.15, 0, NLDASPRECT)
NLDAStime = fa2.time

# No need to convert since data is kg/m2 over 1 hour = mm/hr
NLDASRAIN = NLDASRAIN
NLDASSNOW = NLDASSNOW


# Create simple timeseries plot

fig, ax = plt.subplots()

ax.plot(L15time, L15T, 'c', label='L15') # plotting t, a separately
ax.plot(jratime, jraT, 'm', label='JRA') # plotting t, a separately
ax.plot(e3smtime, e3smT, 'y', label='E3SM') # plotting t, a separately
ax.plot(NLDAStime, NLDAST, 'b', label='NLDAS') # plotting t, a separately
ax.axhline(y=273.15, color='k')

ax.legend()

ax.set(ylim=(258,287))

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H''Z'))
ax.tick_params(axis='x', labelrotation=90)

ax.set_axisbelow(True)
ax.yaxis.grid(color='lightgray', linestyle='dashed')
ax.xaxis.grid(color='lightgray', linestyle='dashed')

left = datetime.date(1996, 1, 17)
right = datetime.date(1996, 1, 21)
plt.gca().set_xbound(left, right)

plt.savefig("timeseries_T_1996event.pdf", format="pdf", bbox_inches="tight")



# Create figure for manuscript

fig, axs = plt.subplots(2, 2)

# Reference width of bars (based on hourly lines)
refer_width = 0.042

# Settings
snow_color='skyblue'
rain_color='green'
temp_color='red'
ref_line_color='k'
bot_t_range=250
top_t_range=290
obs_line_color='b'
obs_line_width=0.75
freezing_temp=273.15

axs[0, 0].bar(L15time, L15SNOW, refer_width*3, label='L15_SNOW', color=snow_color) # plotting t, a separately
axs[0, 0].bar(L15time, L15RAIN, refer_width*3, label='L15_RAIN', color=rain_color) # plotting t, b separately
axs[0, 0].set_title('L15')
ax00 = axs[0, 0].twinx()
ax00.plot(L15time, L15T, temp_color, label='L15') # plotting t, a separately
ax00.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax00.axhline(y=freezing_temp, color=ref_line_color)
ax00.set(ylim=(bot_t_range,top_t_range))
ax00.label_outer()

axs[1, 0].bar(jratime, jraSNOW, refer_width*6, label='JRA_SNOW', color=snow_color) # plotting t, a separately
axs[1, 0].bar(jratime, jraRAIN, refer_width*6, label='JRA_RAIN', color=rain_color) # plotting t, b separately
axs[1, 0].set_title('JRA')
ax10 = axs[1, 0].twinx()
ax10.plot(jratime, jraT, temp_color, label='JRA') # plotting t, a separately
ax10.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax10.axhline(y=freezing_temp, color=ref_line_color)
ax10.set(ylim=(bot_t_range,top_t_range))
ax10.label_outer()

axs[0, 1].bar(NLDAStime, NLDASSNOW, refer_width*1, label='NLDAS_SNOW', color=snow_color) # plotting t, a separately
axs[0, 1].bar(NLDAStime, NLDASRAIN, refer_width*1, label='NLDAS_RAIN', color=rain_color) # plotting t, b separately
axs[0, 1].set_title('NLDAS')
ax01 = axs[0, 1].twinx()
ax01.plot(NLDAStime, NLDAST, temp_color, label='NLDAS') # plotting t, a separately
ax01.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax01.axhline(y=freezing_temp, color=ref_line_color)
ax01.set(ylim=(bot_t_range,top_t_range))
ax01.label_outer()

axs[1, 1].bar(e3smtime, e3smSNOW, (refer_width*3.), label='E3SM_SNOW', color=snow_color) # plotting t, a separately
axs[1, 1].bar(e3smtime, e3smRAIN, (refer_width*3.), label='E3SM_RAIN', color=rain_color) # plotting t, b separately
axs[1, 1].set_title('E3SM')
ax11 = axs[1, 1].twinx()
ax11.plot(e3smtime, e3smT, temp_color, label='E3SM') # plotting t, a separately
ax11.plot(obstime, obsT, obs_line_color, linewidth=obs_line_width)
ax11.axhline(y=freezing_temp, color=ref_line_color)
ax11.set(ylim=(bot_t_range,top_t_range))
ax11.label_outer()

# Do things that apply to all subplots
for ax in axs.flat:
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='lightgray', linestyle='dashed')
    ax.xaxis.grid(color='lightgray', linestyle='dashed')
    ax.set(ylim=(0,4.2))
    ax.set(xlim=(datetime.date(1996, 1, 17),datetime.date(1996, 1, 21)))
    ax.tick_params(axis='x', labelrotation=90)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H''Z'))

for ax in axs.flat:
    ax.set(xlabel='Date (UTC)', ylabel='Precip. rate (mm/hr)')

for ax in axs.flat:
    ax.label_outer()

ax01.set_ylabel('Sfc. temp. (K)')
ax11.set_ylabel('Sfc. temp. (K)')

plt.savefig("precip_vs_t_1996.pdf", format="pdf", bbox_inches="tight")

