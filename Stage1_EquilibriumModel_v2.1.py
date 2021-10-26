#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 14:35:39 2021

@author: andrewhill
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts


# Set out of sample range
#----------------------------------------------------#
outsamp = primary.loc['2018-07-01':'2020-04-01']
insamp = primary.loc[:'2018-04-01']
#----------------------------------------------------#


# Estimate Stage 1 - Equilibrium Model
insamp = insamp.dropna()
y1 = insamp.logrealHPI
x1 = sm.add_constant(insamp[[ 'logrealCC', 'logINC', 'fvyr_pctchg_pop',  'mortgage30',
                         'SB1', 'SB2'
                         ]])

insamp_model = sm.OLS(y1, x1)
insamp_results = insamp_model.fit()
insamp_results.summary() 

# Write estimation results to file for record keeping
pvals = insamp_results.pvalues
coeff = insamp_results.params
conf_lower = insamp_results.conf_int()[0]
conf_higher = insamp_results.conf_int()[1]
results_df = pd.DataFrame({"pvals":pvals,
                               "coeff":coeff,
                               "conf_lower":conf_lower,
                               "conf_higher":conf_higher})
results_df = results_df[["coeff","pvals","conf_lower","conf_higher"]]

#Specify Path
results_df.to_csv(r'')


# Run Engle Granger 2 Step Cointegration Test to ensure cointegrating relationship
def cointegration_test(y, x):
    # Step 1: regress on variable on the other 
    ols_result = sm.OLS(y, x).fit() 
    # Step 2: obtain the residual (ols_resuld.resid)
    # Step 3: apply Augmented Dickey-Fuller test to see whether 
    #        the residual is unit root    
    return ts.adfuller(ols_result.resid)

EngleGranger = cointegration_test(y1, x1)
# As of insamp above, fail to reject null of unit root - BUT p-value is 
# 0.06

insamp['yhat'] = insamp_results.predict(x1)
insamp['resid'] = insamp_results.resid

# Since model depvar is natural log must re-transform using Duan (1983)
duan_smear = np.exp(insamp['resid']).mean()
print(duan_smear)

insamp['Pred_Level_Stage1'] = duan_smear*np.exp(insamp['yhat'])

# Now compute level predictions from out of sample of realHPI
x1_os = sm.add_constant(outsamp[['logrealCC', 'logINC', 'fvyr_pctchg_pop',  'mortgage30',
                         'SB1', 'SB2']])
outsamp['Pred_Level_Stage1'] = duan_smear*np.exp(insamp_results.predict(x1_os))



###---------Generate comparison between IS and OOS  -----------------#
#----- Error metrics for each using describe() ----------------------#
insamp['ForecastError'] = insamp['Pred_Level_Stage1']-insamp['realHPI']
insamp['PercentError'] = (insamp['Pred_Level_Stage1']-insamp['realHPI'])/insamp['realHPI']
insamp['absPercentError'] = np.abs(insamp['Pred_Level_Stage1']-insamp['realHPI'])/insamp['realHPI']

insamp_errormetrics_St1 = insamp[['ForecastError', 'PercentError', 'absPercentError']].describe()

#Specify path
insamp_errormetrics_St1.to_csv(r'')

#--- Do for OOS -----------------------------------------------------#
outsamp['ForecastError'] = outsamp['Pred_Level_Stage1']-outsamp['realHPI']
outsamp['PercentError'] = (outsamp['Pred_Level_Stage1']-outsamp['realHPI'])/outsamp['realHPI']
outsamp['absPercentError'] = np.abs(outsamp['Pred_Level_Stage1']-outsamp['realHPI'])/outsamp['realHPI']

oos_errormetrics_St1 = outsamp[['ForecastError', 'PercentError', 'absPercentError']].describe()

#Specify Path
oos_errormetrics_St1.to_csv(r'')