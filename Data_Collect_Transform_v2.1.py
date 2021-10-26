#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 09:30:16 2021

@author: andrewhill
"""

#First, install relevant packages to the analysis / model dev project

import pandas as pd
import pandas_datareader as pdr
import numpy as np
import statsmodels.api as sm
import datetime as datetime
import plotly.express as px
from fredapi import Fred

#Next, insert user's api_key from FRED 
fred = Fred(api_key='')

# Select whichever time frame of interest to estimate
# fundamental/cointegrating/structural coefficients from

start = datetime.datetime (1947, 1, 1)
end = datetime.datetime (2021, 7, 1)

# Retrieve the following variables from FRED ....
#*--USSTHPI #no conversion needed#
#*--NRATE #qtrl conversion needed#
#*--B230RC0Q173SBEA #no conversion needed#
#*--B011RG3Q086SBEA #no conversion needed#
#*--MORTGAGE30US #conversion needed#
#*--A229RX0Q048SBEA #no conversion needed
#*--CPIAUCSL #conversion needed#


vars1 = pdr.DataReader(['USSTHPI', 'B230RC0Q173SBEA', 'B011RG3Q086SBEA', 'A229RX0Q048SBEA'],
                    'fred', start, end)

#Rename columns for ease of use 

vars1 = vars1.rename(columns={'USSTHPI':'FHFANationalHPI',
                        'B230RC0Q173SBEA':'Population',
                        'B011RG3Q086SBEA':'ConstructionCosts',
                        'A229RX0Q048SBEA':'RealDisposablePCPI'})

#-- Need a loop because of frequency conversion in following tickers -- UNEMP, CPIAUCSL, MRATE30 --#

convertseries = ['UNRATE', 'CPIAUCSL', 'MORTGAGE30US']

vars2 = {} #Create dictionary to store relevant time series
for i in convertseries:
    vars2[i] = fred.get_series(i, start, end, frequency='q')
    vars2 = pd.DataFrame(vars2)  #Combine into dataframe
    print(i)                     #Print for status 

#Combine vars1 with the freq converted vars 2

primary = pd.merge(vars1, vars2, left_index=True, right_index=True)

#----  Convert data series to useful formatting for modeling ----#

#Installing a structural break for HPI trajectory 2000Q1-2007Q1 (boom) and 
# 2007-04-01 - 2012-07-01 (bust)
#Updated on 10/26/2021 to use numpy instead of former logic

primary['SB1'] = \
    np.where((primary.index >= '2000-01-01') & (primary.index <= '2007-01-01'),
             1,
             0)
primary['SB2'] = \
    np.where((primary.index >= '2007-04-01') & (primary.index <= '2012-07-01'),
             1,
             0)
#Note: SBs assigned purely on graphical analysis, not formal statistical testing

#Convert HPI, CC to real terms, and convert mortgage30 to decimal 
primary['realHPI'] = primary['FHFANationalHPI']/primary['CPIAUCSL']*100
primary['realCC'] = primary['ConstructionCosts']/primary['CPIAUCSL']*100
primary['mortgage30'] = primary['MORTGAGE30US']/100

#log where appropriate, create 5 year pop change as a long run population change gauge
primary['logrealHPI'] = np.log(primary['realHPI'])
primary['logrealCC'] = np.log(primary['realCC'])
primary['logINC'] = np.log(primary['RealDisposablePCPI'])
primary['lag_pop_fv_yr'] = primary['Population'].shift(20)
primary['fvyr_pctchg_pop'] = (primary['Population']-primary['lag_pop_fv_yr'])/primary['lag_pop_fv_yr']


#Please progress to the next module 