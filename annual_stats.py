import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import sys
import os

basin_shape=str(sys.argv[1]) # What is the basin flag?

DATADIR="./output/"+basin_shape

## Simple script to check annual snowfall correlations between data products
add_avg=False

jra = np.genfromtxt(DATADIR+'/csv/JRA_yearly_total_SWE.csv', delimiter=',')
l15 = np.genfromtxt(DATADIR+'/csv/L15_yearly_total_SWE.csv', delimiter=',')
e3sm = np.genfromtxt(DATADIR+'/csv/E3SM_yearly_total_SWE.csv', delimiter=',')
nldas = np.genfromtxt(DATADIR+'/csv/NLDAS_yearly_total_SWE.csv', delimiter=',')

if (add_avg):
    mean = np.mean([jra,l15,e3sm,nldas], axis=0)

print(stats.pearsonr(jra, l15))
print(stats.pearsonr(jra, e3sm))
print(stats.pearsonr(jra, nldas))
print(stats.pearsonr(l15, e3sm))
print(stats.pearsonr(l15, nldas))
print(stats.pearsonr(e3sm, nldas))

styr=1984
enyr=2005
years = range(styr, enyr+1, 1)

fig, ax = plt.subplots(1, 1, figsize = (8, 4))
ax.set_ylim(0, 410)
ax.margins(x=0)
ax.xaxis.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha = 0.8)

ax.plot(years, jra, color = "#CC79A7", label = "JRA", linewidth=2.0, alpha = 0.6)
ax.plot(years, l15, color = "#009E73", label = "L15", linewidth=2.0, alpha = 1.0)
ax.plot(years, e3sm, color = "#E69F00", label = "E3SM", linewidth=2.0, alpha = 0.8)
ax.plot(years, nldas, color = "crimson", label = "NLDAS", linewidth=2.0)
if (add_avg):
    ax.plot(years, mean, color = "black", linestyle='--', label = "avg", linewidth=1.0)

ax.set_xticks(np.arange(styr,enyr,2))

ax.set_xlabel("Water year")
ax.set_ylabel("Positive dSWE sum (mm)")

ax.legend()
ax.set_title("Interannual snowfall totals")

if not os.path.exists(DATADIR+'/diag/'):
    os.makedirs(DATADIR+'/diag/')
fig.savefig(DATADIR+'/diag/SWE_totals.pdf')

plt.close()