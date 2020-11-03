import yfinance as yf 
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
from datetime import datetime
from scipy.stats import norm

query = yf.Ticker('AUDUSD=X') 
df = query.history(start='2018-01-01', end=pd.datetime.now())

#Weighted moving average with decay factor 
fast = 10
slow = 30 

df['EMA10'] = df['Close'].ewm(fast).mean() 
df['EMA10YTD'] = df['EMA10'].shift(1) #avoid timestamp iterating in logical statement 
df['EMA30'] = df['Close'].ewm(slow).mean()
df['EMA30YTD'] = df['EMA30'].shift(1) 

df['Buy/Sell'] = [1 if (df.loc[i, 'EMA10YTD'] < df.loc[i,'EMA30YTD']) & (df.loc[(i), 'EMA10'] > df.loc[(i), 'EMA30']) else -1 if (df.loc[i, 'EMA10YTD'] > df.loc[i,'EMA30YTD']) & (df.loc[(i), 'EMA10'] < df.loc[(i), 'EMA30']) else 0 for i in df.index] 
#logic: Sell (1) if previous day's fast < slow AND today's fast > slow (upward cut) and vv.
print(df) 

signals = df['Buy/Sell'].tolist() 
buy = signals.count(1) 
sell = signals.count(-1) 

print('Total Buy Signals: ' + str(buy))
print('Total Sell Signals: ' + str(sell))
#combining all sell/buy signals into overview 

#log_returns function 
def log_returns(price_param, df): 
    df['Log Returns'] = np.log(df[price_param])- np.log(df[price_param].shift(1))
    df = df.dropna()

    mu = df['Log Returns'].mean() 
    sigma = df['Log Returns'].std(ddof=1) 
    
    return df, mu, sigma 

#probability (CDF) from normal dist. function 
def distribution(pnl_range, mu, sigma): 
    likelihood = pd.DataFrame() 
    likelihood['Profit/Loss (%)'] = pnl_range 
    likelihood = likelihood.set_index('Profit/Loss (%)')
    probability = []
    for x in pnl_range: 
        prob = norm.cdf((x/100), mu, sigma) 
        probability.append(prob) 
    likelihood['Probability'] = probability 
    return likelihood 

df_select = df.loc[datetime(2020, 5, 1):, :]
print(df_select)
df_select, mu, sigma = log_returns('Close', df) 
loss = distribution([-1,-2,-3,-4,-5], mu, sigma) 
profit = distribution([1,2,3,4,5], mu, sigma)
print(loss)
print(profit) 
#Negative returns probability during price hike after "buy' signal is interesting

#next steps
#Ranjan - Calculating portfolio returns trading solely with this strategy 
#Nilay - Combine with Bollinger Band 
#Leoni - Potential strategies with probability

#visualising 
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(df['Close'], color='b') 
plt.plot(df['EMA10'], color='r')
plt.plot(df['EMA30'], color='g')

plt.xlabel('Date') 
plt.ylabel('Price in $') 
plt.show() 