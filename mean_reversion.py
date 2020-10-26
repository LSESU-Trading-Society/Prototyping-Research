'''LSESU TRADING SOCIETY 2020/2021
Mean Reverting Strategy based on Daily Log Returns Distribution
Contributors: Nilay Jagtap, Ranjan RJ, Leoni Externest and Phuong Dang
Date: 26/10/2020'''

#import all necessary libraries 
import yfinance as yf 
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
from datetime import datetime 
from scipy.stats import kurtosistest


#QUERY DATA / CLEAN + PROCESS 
ticker = 'QDEL' #QUIDEL 
query = yf.Ticker(ticker) #instantiating Ticker object, feeding it our ticker
df = query.history(start=datetime(2020, 5, 1), end=datetime(2020,10,10))  #querying data, datetime() formats our dates into readable time series date
df['Log Returns'] = (np.log(df['Close']) - np.log(df['Close'].shift(1)))/np.log(df['Close'].shift(1)) #calculating log returns for all close prices 
df = df.dropna() #drop null values to avoid future calculation errors 
print(df) 

mean_close = df['Close'].mean() #finding the mean close price (exploratory purposes) 
print(mean_close) 

#VISUALISING SECURITY PRICES
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(df['Close']) 
plt.axhline(mean_close, linestyle='--', color='r')
plt.show() #visualising security prices & its mean --> determining it is roughly oscilatting about one mean

#PROBABILITY DISTRIBUTION 
result = kurtosistest(df['Log Returns']) #normal Kurtosis score is 3 
#QDEL's value is 5.02 --> "relatively normal" 

sns.set() 
plt.figure(figsize = (10,10)) 
plt.hist(df['Log Returns'], bins = 20) #visualising probability distrbution of log returns in bins of 20
plt.show() 

mu = df['Log Returns'].mean() #returns mean
sigma = df['Log Returns'].std(ddof=1) #returns std 

#Formula for z-score: z = x - mu / sigma 


df2 = pd.DataFrame() #creating new df 
df2['Close'] = df['Close'] #close prices
df2['X'] = df['Log Returns'] #log returns 
df2['Z-Score'] = (df2['X'] - mu) / sigma  #calculate z-score
#Generate signals based on z-score
#pseudocode: Enter short position if the log daily returns is (+) and exceed 2 standard deviations. Enter position if the log daily returns is (-) and exceed 2 standard deviations.
df2['Outlier Short'] = [1 if df2.loc[i, 'Z-Score'] > 2 else 0 for i in df2.index]
df2['Outlier Long'] = [1 if df2.loc[i, 'Z-Score'] < -2 else 0 for i in df2.index]

short_count = df2['Outlier Short'].sum() #counting all short/long signals 
long_count = df2['Outlier Long'].sum() 

date_short = df2.index[df2['Outlier Short'] == 1].tolist() #extract short/long signals date
date_long = df2.index[df2['Outlier Long'] == 1].tolist() 

print(df2)
print(short_count) 
print(long_count)
print(date_short)
print(date_long) 