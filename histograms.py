#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
#plt.style.use('seaborn-white')


# In[ ]:


csv_file = "./output/supercat.csv"

which_thresh  = '-1.0'
#which_thresh = '95.0'

## Essentially hardcoded...
outputdir="./output/"
histdir = "./hists/"

# Figure out how to label output
if float(which_thresh) > 0.0:
    perclabel = str(int(percFilter))
else:
    perclabel = "AB"
    
# In[3]:


raw_df = pd.read_csv(csv_file)

#raw_df.head


# In[4]:

## If output subdir doesn't exist, create it.
if not os.path.exists(histdir):
    os.makedirs(histdir)

df = raw_df

sub_df = df[df['Thresh'] == which_thresh]

varlist = ['wt_rof','st_swe','Event Length', 'Average dSWE', 'Max dSWE', 'Average Runoff', 'Max Runoff', 'Average Precip', 'Max Precip']

length_written=False
thresh_written=False

columns = ["E3SM", "JRA", "L15", "NLDAS"]

outdf = pd.DataFrame()

for var in varlist:
    
    x1 = sub_df.loc[df['Dataset'] == 'E3SM'][var].values.astype(float)
    x2 = sub_df.loc[df['Dataset'] == 'JRA'][var].values.astype(float)
    x3 = sub_df.loc[df['Dataset'] == 'L15'][var].values.astype(float)
    x4 = sub_df.loc[df['Dataset'] == 'NLDAS'][var].values.astype(float)

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

## Write stats to CSV
outdf.to_csv(outputdir+"/table_stats_"+perclabel+".csv")


# In[5]:


plotvarlist = ['wt_rof','st_swe','Event Length', 'Average dSWE', 'Max dSWE', 'Average Runoff', 'Max Runoff', 'Average Precip', 'Max Precip']

for var in varlist:

    print(var)
    #var="Max dSWE"

    NBINS=8

    x1 = sub_df.loc[df['Dataset'] == 'E3SM'][var].values.astype(float)
    x2 = sub_df.loc[df['Dataset'] == 'JRA'][var].values.astype(float)
    x3 = sub_df.loc[df['Dataset'] == 'L15'][var].values.astype(float)
    x4 = sub_df.loc[df['Dataset'] == 'NLDAS'][var].values.astype(float)

    #kwargs = dict(histtype='stepfilled', alpha=0.3, density=True, bins=6, ec="k", linewidth=2.0)

    kwargs = dict(histtype='step', bins=NBINS, alpha=0.75)

    weights = np.ones_like(x1) / len(x1)
    plt.hist(x1, **kwargs, weights=weights, linewidth=1.0, color='black', label="E3SM")

    weights = np.ones_like(x2) / len(x2)
    plt.hist(x2, **kwargs, weights=weights, linewidth=1.7, color='orange', label="JRA")

    weights = np.ones_like(x3) / len(x3)
    plt.hist(x3, **kwargs, weights=weights, linewidth=2.3, color='mediumslateblue', label="L15")

    weights = np.ones_like(x4) / len(x4)
    plt.hist(x4, **kwargs, weights=weights, linewidth=3.1, color='lightskyblue', label="NLDAS");

    plt.legend(loc="upper right")

    plt.suptitle(var)
    plt.ylabel("PDF (%)")
    plt.xlabel("mm/day")

    newstr=var.replace(" ", "_")
    
    #plt.show()
    plt.savefig(histdir+"/"+newstr+".pdf")
    plt.close()


# In[6]:


events=outdf['Num']

kwargs = dict(histtype='step', bins=NBINS, alpha=0.75)

x = outdf.index
events=outdf['Num']

x_pos = [i for i, _ in enumerate(x)]

plt.bar(x_pos, events, color=('black','orange','mediumslateblue','lightskyblue'))

plt.xticks(x_pos, x)

plt.suptitle("Events")
plt.ylabel("Number events")
plt.xlabel("Data Product")

#plt.show()
newstr="events"
plt.savefig(histdir+"/"+newstr+".pdf")
plt.close()




