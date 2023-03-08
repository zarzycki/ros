import numpy as np
from datetime import datetime
import pandas as pd
import xarray as xr
import scipy.stats as stats
import os

OUTPUTDIR="corr_stats"
PRINT_ALL_MATRICES=False  ## Print other offsets to verify nothing is +/- 1 day, etc.
#-------

## Define some functions
def is_winter(month):
    return (month >= 11) | (month <= 4)

def is_summer(month):
    return (month >= 6) & (month <= 9)

#-------

# Open data
jra = xr.open_dataset("./netcdf/JRA_1985to2005_masked.nc")
l15 = xr.open_dataset("./netcdf/L15_1985to2005_masked.nc")
nldas = xr.open_dataset("./netcdf/NLDAS_1985to2005_masked.nc")
e3sm = xr.open_dataset("./netcdf/E3SM_1985to2005_masked.nc")

## If output subdir doesn't exist, create it.
if not os.path.exists(OUTPUTDIR):
    os.makedirs(OUTPUTDIR)

jrawgt = np.cos(np.deg2rad(jra["lat"]))
jrawgt.name = "weights"
jrapre = jra["PRECIP"].weighted(jrawgt).mean(dim = ["lat", "lon"], skipna=True)
jrarof = jra["ROF"].weighted(jrawgt).mean(dim = ["lat", "lon"], skipna=True)
jradswe = jra["SWE"].weighted(jrawgt).mean(dim = ["lat", "lon"], skipna=True)

l15wgt = np.cos(np.deg2rad(l15["lat"]))
l15wgt.name = "weights"
l15pre = l15["PRECIP"].weighted(l15wgt).mean(dim = ["lat", "lon"], skipna=True)
l15rof = l15["ROF"].weighted(l15wgt).mean(dim = ["lat", "lon"], skipna=True)
l15dswe = l15["SWE"].weighted(l15wgt).mean(dim = ["lat", "lon"], skipna=True)

nldaswgt = np.cos(np.deg2rad(nldas["lat"]))
nldaswgt.name = "weights"
nldaspre = nldas["PRECIP"].weighted(nldaswgt).mean(dim = ["lat", "lon"], skipna=True)
nldasrof = nldas["ROF"].weighted(nldaswgt).mean(dim = ["lat", "lon"], skipna=True)
nldasdswe = nldas["SWE"].weighted(nldaswgt).mean(dim = ["lat", "lon"], skipna=True)

e3smwgt = np.cos(np.deg2rad(e3sm["lat"]))
e3smwgt.name = "weights"
e3smpre = e3sm["PRECIP"].weighted(e3smwgt).mean(dim = ["lat", "lon"], skipna=True)
e3smrof = e3sm["ROF"].weighted(e3smwgt).mean(dim = ["lat", "lon"], skipna=True)
e3smdswe = e3sm["SWE"].weighted(e3smwgt).mean(dim = ["lat", "lon"], skipna=True)


## Check correlations

preoffzero = pd.DataFrame({"JRA": jrapre, "L15": l15pre, "NLDAS": nldaspre, "E3SM": e3smpre});
preoffonejra = pd.DataFrame({"JRA": jrapre[1::], "L15": l15pre[:-1:], "NLDAS": nldaspre[:-1:], "E3SM": e3smpre[:-1:]})
preoffnegonejra = pd.DataFrame({"JRA": jrapre[:-1:], "L15": l15pre[1::], "NLDAS": nldaspre[1::], "E3SM": e3smpre[1::]})

preoffonel15 = pd.DataFrame({"JRA": jrapre[:-1:], "L15": l15pre[1::], "NLDAS": nldaspre[:-1:], "E3SM": e3smpre[:-1:]})
preoffonenldas = pd.DataFrame({"JRA": jrapre[:-1:], "L15": l15pre[:-1:], "NLDAS": nldaspre[1::], "E3SM": e3smpre[:-1:]})
preoffonee3sm = pd.DataFrame({"JRA": jrapre[:-1:], "L15": l15pre[:-1:], "NLDAS": nldaspre[:-1:], "E3SM": e3smpre[1::]})

if PRINT_ALL_MATRICES:
	preoffzero.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffzerocorr.csv")
	preoffonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffonejracorr.csv")
	preoffnegonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffnegonejracorr.csv")
	preoffonel15.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffonel15corr.csv")
	preoffonenldas.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffonenldascorr.csv")
  preoffonee3sm.corr(method = "pearson").to_csv(OUTPUTDIR+"/preoffonee3smcorr.csv")


rofoffzero = pd.DataFrame({"JRA": jrarof, "L15": l15rof, "NLDAS": nldasrof, "E3SM": e3smrof});
rofoffonejra = pd.DataFrame({"JRA": jrarof[1::], "L15": l15rof[:-1:], "NLDAS": nldasrof[:-1:], "E3SM": e3smrof[:-1:]})
rofoffnegonejra = pd.DataFrame({"JRA": jrarof[:-1:], "L15": l15rof[1::], "NLDAS": nldasrof[1::], "E3SM": e3smrof[1::]})

rofoffonel15 = pd.DataFrame({"JRA": jrarof[:-1:], "L15": l15rof[1::], "NLDAS": nldasrof[:-1:], "E3SM": e3smrof[:-1:]})
rofoffonenldas = pd.DataFrame({"JRA": jrarof[:-1:], "L15": l15rof[:-1:], "NLDAS": nldasrof[1::], "E3SM": e3smrof[:-1:]})
rofoffonee3sm = pd.DataFrame({"JRA": jrarof[:-1:], "L15": l15rof[:-1:], "NLDAS": nldasrof[:-1:], "E3SM": e3smrof[1::]})

if PRINT_ALL_MATRICES:
	rofoffzero.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffzerocorr.csv")
	rofoffonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffonejracorr.csv")
	rofoffnegonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffnegonejracorr.csv")
	rofoffonel15.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffonel15corr.csv")
	rofoffonenldas.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffonenldascorr.csv")
  rofoffonee3sm.corr(method = "pearson").to_csv(OUTPUTDIR+"/rofoffonee3smcorr.csv")


dsweoffzero = pd.DataFrame({"JRA": jradswe, "L15": l15dswe, "NLDAS": nldasdswe, "E3SM": e3smdswe});
dsweoffonejra = pd.DataFrame({"JRA": jradswe[1::], "L15": l15dswe[:-1:], "NLDAS": nldasdswe[:-1:], "E3SM": e3smdswe[:-1:]})
dsweoffnegonejra = pd.DataFrame({"JRA": jradswe[:-1:], "L15": l15dswe[1::], "NLDAS": nldasdswe[1::], "E3SM": e3smdswe[1::]})

dsweoffonel15 = pd.DataFrame({"JRA": jradswe[:-1:], "L15": l15dswe[1::], "NLDAS": nldasdswe[:-1:], "E3SM": e3smdswe[:-1:]})
dsweoffonenldas = pd.DataFrame({"JRA": jradswe[:-1:], "L15": l15dswe[:-1:], "NLDAS": nldasdswe[1::], "E3SM": e3smdswe[:-1:]})
dsweoffonee3sm = pd.DataFrame({"JRA": jradswe[:-1:], "L15": l15dswe[:-1:], "NLDAS": nldasdswe[:-1:], "E3SM": e3smdswe[1::]})

if PRINT_ALL_MATRICES:
	dsweoffzero.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffzerocorr.csv")
	dsweoffonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffonejracorr.csv")
	dsweoffnegonejra.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffnegonejracorr.csv")
	dsweoffonel15.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffonel15corr.csv")
	dsweoffonenldas.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffonenldascorr.csv")
  dsweoffonee3sm.corr(method = "pearson").to_csv(OUTPUTDIR+"/dsweoffonee3smcorr.csv")


### Check p values
print("PRECIP")
print("JRA+L15: ",stats.pearsonr(jrapre[:-1:],l15pre[:-1:]))
print("JRA+NLDAS: ",stats.pearsonr(jrapre[:-1:],nldaspre[:-1:]))
print("JRA+E3SM: ",stats.pearsonr(jrapre[:-1:],e3smpre[1::]))
print("NLDAS+L15: ",stats.pearsonr(nldaspre[:-1:],l15pre[:-1:]))
print("NLDAS+E3SM: ",stats.pearsonr(nldaspre[:-1:],e3smpre[1::]))
print("E3SM+L15: ",stats.pearsonr(e3smpre[1::],l15pre[:-1:]))

print("ROF")
print("JRA+L15: ",stats.pearsonr(jrarof[:-1:],l15rof[:-1:]))
print("JRA+NLDAS: ",stats.pearsonr(jrarof[:-1:],nldasrof[:-1:]))
print("JRA+E3SM: ",stats.pearsonr(jrarof[:-1:],e3smrof[1::]))
print("NLDAS+L15: ",stats.pearsonr(nldasrof[:-1:],l15rof[:-1:]))
print("NLDAS+E3SM: ",stats.pearsonr(nldasrof[:-1:],e3smrof[1::]))
print("E3SM+L15: ",stats.pearsonr(e3smrof[1::],l15rof[:-1:]))

print("dSWE")
print("JRA+L15: ",stats.pearsonr(jradswe[:-1:],l15dswe[:-1:]))
print("JRA+NLDAS: ",stats.pearsonr(jradswe[:-1:],nldasdswe[:-1:]))
print("JRA+E3SM: ",stats.pearsonr(jradswe[:-1:],e3smdswe[1::]))
print("NLDAS+L15: ",stats.pearsonr(nldasdswe[:-1:],l15dswe[:-1:]))
print("NLDAS+E3SM: ",stats.pearsonr(nldasdswe[:-1:],e3smdswe[1::]))
print("E3SM+L15: ",stats.pearsonr(e3smdswe[1::],l15dswe[:-1:]))

