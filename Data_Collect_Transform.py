#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 16:10:39 2021

@author: andrewhill
"""


#----- Variable Key -----#
#*--USSTHPI #no conversion needed#
#*--NRATE #qtrl conversion needed#
#*--B230RC0Q173SBEA #no conversion needed#
#*--B011RG3Q086SBEA #no conversion needed#
#*--MORTGAGE30US #conversion needed#
#*--A229RX0Q048SBEA #no conversion needed
#*--CPIAUCSL #conversion needed#

#pip install pandas-datareader
#pip install fredapi
#API KEY 569c71585b0ad966865c50758b492cf5
#pip install plotly.express
#sp = fred.get_series('USSTHPI',	'CPIAUCSL',	'ATNHPIUS45300Q','ATNHPIUS12060Q')

import pandas as pd
import pandas_datareader as pdr
import numpy as np
import statsmodels.api as sm
import datetime 
import plotly.express as px
from fredapi import Fred
fred = Fred(api_key='569c71585b0ad966865c50758b492cf5')

start = datetime.datetime (1947, 1, 1)
end = datetime.datetime (2020, 7, 1)

vars1 = pdr.DataReader(['USSTHPI', 'B230RC0Q173SBEA', 'B011RG3Q086SBEA', 'A229RX0Q048SBEA'],
                    'fred', start, end)
vars1 = vars1.rename(columns={'USSTHPI':'FHFANationalHPI',
                        'B230RC0Q173SBEA':'Population',
                        'B011RG3Q086SBEA':'ConstructionCosts',
                        'A229RX0Q048SBEA':'RealDisposablePCPI'})

#-- Need a loop because of frequency conversion in following tickers -- UNEMP and CPIAUCSL --#

convertseries = ['UNRATE', 'CPIAUCSL', 'MORTGAGE30US']
vars2 = {}
for i in convertseries:
    vars2[i] = fred.get_series(i, start, end, frequency='q')
    vars2 = pd.DataFrame(vars2)
    print(i)
    
master = pd.merge(vars1, vars2, left_index=True, right_index=True)

#----  Convert data series to useful formatting for modeling ----#

master['SB_2000Q1_2007Q1'] = \
            ((master.index >= '2000-01-01') & 
           (master.index <= '2007-01-01')).astype(int)


master['SB_2007Q2_2012Q3'] = \
            ((master.index >= '2007-04-01') & 
             (master.index <= '2012-07-01')).astype(int)

master['realHPI'] = master['FHFANationalHPI']/master['CPIAUCSL']*100
master['realCC'] = master['ConstructionCosts']/master['CPIAUCSL']*100
master['mortgage30'] = master['MORTGAGE30US']/100

master['logrealHPI'] = np.log(master['realHPI'])
master['logrealCC'] = np.log(master['realCC'])
master['logINC'] = np.log(master['RealDisposablePCPI'])
master['lag_pop_fv_yr'] = master['Population'].shift(20)
master['fvyr_pctchg_pop'] = (master['Population']-master['lag_pop_fv_yr'])/master['lag_pop_fv_yr']


#--- Next project - iteratively assign OS and generate metrics ----#
#os = master.loc['2018-01-01':'2020-07-01']

master['counter'] = range(1, len(master)+1)
len(master)

for i in range(150, 175):
    
    dftst = master.loc[master["counter"]<i]
    print(i)
    
    
dftst = master.loc[master["counter"]>=100]
    
dict_regsets = {}
for i in range(150,155):
    df_tst = master.loc[master["counter"]<=i]
    dict_regsets['df_' + str(i)] = df_tst
    
newdat = dict_subsets['df_151']