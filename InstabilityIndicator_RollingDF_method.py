#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 20:21:12 2021

@author: andrewhill
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS



maxtime = 1000
tlist = []

for j in range(0, 10000):
    
    price_path = [0]
    
    for t in range(0, maxtime+1):
        if t < 500:
            alpha = 0.80
        elif t > 550:
            alpha = .80
        else:
            alpha = 1.0

        price_path[t] = alpha*price_path[t-1] + np.random.normal(loc=0, scale=1.0)
        price_path.append(price_path[t])
    
    path = pd.DataFrame(price_path)
    path.columns = ['Yt']
    path['Yt_1'] = path['Yt'].shift(1)
    path['dYt'] = path['Yt'].diff()

    simdat = path.dropna()

    rolldat = simdat.dropna()
    rollX = rolldat['Yt_1']
    rollY = rolldat['dYt']

    mod = RollingOLS(rollY, rollX, window=50)
    rolling_res = mod.fit()
   
    tvals = rolling_res.tvalues
    tvals[j] = tvals.dropna()
    tlist.append(tvals[j])

tst = pd.DataFrame(tlist)

pctls = tst.quantile([0.10, 0.05, 0.025, 0.01])


""" do a case by case analysis on the above, figure out the issue """

#for j in range(0, 100):
    
price_path = [0]

for t in range(0, 100000):
    #if t < 500:
    #    alpha = 0.85
    #elif t > 550:
    #    alpha = 0.85
    #else:
        alpha = 1.0
        
        price_path[t] = alpha*price_path[t-1] + np.random.normal(loc=0, scale=1.0)
    
        price_path.append(price_path[t])
    
path = pd.DataFrame(price_path)
path.columns = ['Yt']
path['Yt_1'] = path['Yt'].shift(1)
path['dYt'] = path['Yt'].diff()

dat = path.dropna()
    
rollx = dat['Yt_1']
rollY = dat['dYt']
mod = RollingOLS(rollY, rollx, window=50)
rolling_res = mod.fit()

tvalue = rolling_res.tvalues

tvalue2 = tvalue.dropna()

tstpct = np.percentile(tvalue2, [10, 5, 2.5, 1])

""" use OLS only, straight time series MC, no roll """

#for trial in range(0, 10000):
tlst = []
for trial in range(0, 10000):        
    price_path = [0]
    for t in range(0, 51):
        price_path[t] = 1.0*price_path[t-1] + np.random.normal(loc=0, scale=1.0)
        price_path.append(price_path[t])
            
    path = pd.DataFrame(price_path)
    path.columns = ['Yt']
    path['Yt_1'] = path['Yt'].shift(1)
    path['dYt'] = path['Yt'].diff()
            
    dat = path.dropna()
    x = dat['Yt_1']
    y = dat['dYt']
    mod = sm.OLS(y, x).fit()
    mod.summary()
    tval = mod.tvalues
    tlst.append(tval)
    
tdf = pd.DataFrame(tlst)

tstpct = np.percentile(tdf, [10, 5, 2.5, 1])

""" same as above, now do RollingOLS and see tval list """

price_path = [0]
for t in range(0, 500):
    price_path[t] = 1.0*price_path[t-1] + np.random.normal(loc=0, scale=1.0)
    price_path.append(price_path[t])
    
path = pd.DataFrame(price_path)
path.columns = ['Yt']
path['Yt_1'] = path['Yt'].shift(1)
path['dYt'] = path['Yt'].diff()

dat = path.dropna()

x = dat['Yt_1']
y = dat['dYt']

mod = RollingOLS(y, x, window=50).fit()
#rolling_res = mod.fit()

tvalue = mod.tvalues
parms = mod.params