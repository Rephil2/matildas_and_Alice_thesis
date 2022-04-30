import statsmodels.api as sm
from scipy import stats as st
import pandas as pd
import numpy as np
import math
####
## Function Definitions
####

def has_nan_values(listValues, it):
    # Check for nan values 
    nan_values = np.where(np.array(listValues) == "nan")
    if len(nan_values[0]) > 0: 
        print("Stock " +str(it)+ " in row: " + str(it*3) + " disregarded. nan values present")
        return True
    
    # make sure values recieved are readable and not "#ERROR,$$ER: 2361NO DATA AVAILABLE" f.x.
    if not isinstance(listValues[2], str):
        print("Stock " +str(it)+ " in row: " + str(it*3) + " did not compute correctly")
        return True
    
    # if everything looks good return false
    return False

def get_omxpi_values(df_omxpi, dates):
    # Description takes a list of date and returns respective OMXPI values
    OMXPI_values=["OMXPI"]
    prev_val=0
    for date in dates[1:]: 
        if date == "NaN":
            OMXPI_values.append("NaN")
            continue
        try: value = float(df_omxpi.loc[df_omxpi['Unnamed: 1'] == str(date)]["Unnamed: 2"])
        except: value = prev_val
        prev_val = value
        OMXPI_values.append(value)
    return OMXPI_values

def stock_return_values(StockValues):
    # Returns stock return values
    prev_value = 0.0
    stock_return_values=["StockReturn"]
    for value in StockValues[1:]:
        try:stock_return_values.append(math.log(value / prev_value))
        except:stock_return_values.append(0.0)
            
        prev_value = value
    return stock_return_values

def market_return_values(MarketValues):
    # Returns Market return values
    prev_value = 0.0
    market_return_values=["MarketReturn"]
    for value in MarketValues[1:]:
        try:market_return_values.append(np.log(float(value) / float(prev_value)))
        except:market_return_values.append(0.0)
        prev_value = value
    return market_return_values

def get_windows(df, thres):
    # splits the stock into an estimation window and event window based thres(threshold)
    estimatation_window = df.iloc[:, 0:thres]
    event_window = df.iloc[:, thres:]
    est_win_size = estimatation_window.shape[1]-1 #-1 to exclude name row 
    eve_win_size = event_window.shape[1]
    return est_win_size, estimatation_window, eve_win_size, event_window


def normal_return_values(MarketValues, slope, intercept):
    normal_return = ["NormalReturn"]
    for mr in MarketValues:
        if mr == 0.0: 
            normal_return.append(0)
            continue
        normal_return.append(intercept + (slope * mr))
    return normal_return

def linear_regression(x,y):
    X = sm.add_constant(x) # intercept
    model = sm.OLS(y, X)
    fit = model.fit()
    stderr = np.sqrt(fit.mse_resid)
    intercept, slope = fit.params
    #fit.rsquared
    return intercept, slope, stderr

def t_stat_r(abnormal_return, stderr):
    tstat_r = np.array(abnormal_return) / stderr
    tstat_r = tstat_r.tolist()
    tstat_r.insert(0,"t-stat R")
    return tstat_r

def mean(df, thres):
    df_means = df.mean()
    means = df_means[thres-1:].to_list() # Columns
    df_means[thres:].mean() # window
    return means

def st_dev(df, thres):
    df_stds = df.std()
    stds = df_stds[thres-1:].to_list() # Columns 
    df_stds[thres:].std() # window
    return stds

def t_test(df, event_size, thres):
    aar_tstats, aar_pvalues = [],[]
    thres = thres
    for it in range(event_size):
        it = it + thres
        tstat = st.ttest_1samp(df[it].to_numpy(),popmean=0)
        aar_tstats.append(tstat[0])
        aar_pvalues.append(tstat[1])
    return aar_tstats, aar_pvalues