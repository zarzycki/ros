import numpy as np
import scipy.stats as stats

## Simple script to check annual snowfall correlations between data products

jra = np.genfromtxt('./output/JRA_yearly_total_SWE.csv', delimiter=',')
l15 = np.genfromtxt('./output/L15_yearly_total_SWE.csv', delimiter=',')
e3sm = np.genfromtxt('./output/E3SM_yearly_total_SWE.csv', delimiter=',')
nldas = np.genfromtxt('./output/NLDAS_yearly_total_SWE.csv', delimiter=',')

print(stats.pearsonr(jra, l15))
print(stats.pearsonr(jra, e3sm))
print(stats.pearsonr(jra, nldas))
print(stats.pearsonr(l15, e3sm))
print(stats.pearsonr(l15, nldas))
print(stats.pearsonr(e3sm, nldas))