import yfinance as yf 
import pandas as pd
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint


#energy: oil/gas - esg 
#Exxon - another energy company/index + XLE XOM 
#Semiconductors - intel AMD Nvidia Xilink 

#cointegration --> XOM/XLE -- REGI/XLE 
#visualising 
'''
ticker_list = ['XOM', 'REGI', 'XLE', 'BP', '^CELS', 'CVX', 'ICLN']

for i in ticker_list: 
    query = yf.Ticker(i) 
    i = query.history(start='2018-01-01', end=pd.datetime.now())
    print(i)'''

ticker = yf.Ticker('REGI') 
etf = yf.Ticker('XLE') 

df_ticker = ticker.history(start='2016-01-01', end='2020-01-01')
df_etf = etf.history(start='2016-01-01', end='2020-01-01')

'''sns.set() 
plt.figure(figsize = (10,10)) 
plt.plot(df_ticker['Close'], color='b') 
plt.plot(df_etf['Close'], color='r') 
plt.show() '''

df_ticker['Log Returns'] = np.log(df_ticker['Close']) # - np.log(df_ticker['Close'].shift(1))
df_etf['Log Returns'] = np.log(df_etf['Close']) #- np.log(df_ticker['Close'].shift(1))
df_ticker = df_ticker.dropna() 
df_etf = df_etf.dropna() 

print(df_ticker) 
print(df_etf) 

spread = pd.DataFrame() 
spread['Spread'] = (df_ticker['Log Returns'] - df_etf['Log Returns'])
print(spread)
mean = spread['Spread'].mean() 

sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(spread['Spread'], color='b')
plt.axhline(mean, linestyle='--', color='r')
#plt.axhline((df_ticker['Log Returns'] - df_etf['Log Returns']).mean(), color='r', linestyle='--')
plt.show() 

score, pvalues, _ = coint(df_ticker['Close'], df_etf['Close'])
print(pvalues) 

#how to pick a time period - when would you decide that they're following a pattern 
#find more tickers to look 
#more coint tests
#signal generation 

