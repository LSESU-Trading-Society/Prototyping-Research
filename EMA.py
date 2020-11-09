import yfinance as yf 
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
from datetime import datetime
from scipy.stats import norm
from datetime import datetime

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

def timedelta(buy_dates: list, sell_dates: list) -> list: 
    holding_days = [] 
    for d in range(len(buy_dates)): 
        delta = sell_dates[d] - buy_dates[d]
        holding_days.append(delta)
    return holding_days

def timedelta_from_dataframe(df) -> int: 
    delta = df.index[-1] - df.index[0] 
    return delta.days

def match_buy_sell_dates(buy_dates: list , sell_dates: list) -> list: 
    if len(buy_dates) < len(sell_dates): 
        del sell_dates[0] 
        holding_days = timedelta(buy_dates, sell_dates)
        return holding_days   
    elif len(buy_dates) > len(sell_dates) : 
        del buy_dates[-1] 
        holding_days = timedelta(buy_dates, sell_dates)
        return holding_days
    else: 
        holding_days = timedelta(buy_dates, sell_dates)
        return holding_days

def calculate_periodic_volatility(df, period: int): 
    sigma = df['Log Returns'].std(ddof=1) 
    volatility = sigma * (period**0.5)
    return volatility

query = yf.Ticker('ATVI') 
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

buy_dates = df.index[df['Buy/Sell'] == 1].tolist() 
sell_dates = df.index[df['Buy/Sell'] == -1].tolist()
holding_days = match_buy_sell_dates(buy_dates, sell_dates) 

sell_buy_pairs = dict(zip(buy_dates, sell_dates))
print(sell_buy_pairs)
#key: buy date 

#iterate through to find prob distrbution + volatility 
#read documentation on dictionary syntaxes
'''
df_select = df.loc[datetime(2020, 5, 1):, :]
print(df_select)
df_select, mu, sigma = log_returns('Close', df) 
loss = distribution([-1,-2,-3,-4,-5], mu, sigma) 
profit = distribution([1,2,3,4,5], mu, sigma)
print(loss)
print(profit) '''
#Negative returns probability during price hike after "buy' signal is interesting

for start, end in sell_buy_pairs.items(): 
    df_cut = df[(start):(end)]
    df_cut, mu, sigma = log_returns('Close', df_cut) 

    period = timedelta_from_dataframe(df_cut) 

    loss = distribution([-1,-2,-3,-4,-5], mu, sigma) 
    profit = distribution([1,2,3,4,5], mu, sigma)

    volatility = calculate_periodic_volatility(df_cut, period) 

    print('Period from ' + str(start) + ' to ' + str(end)) 
    print('Length: ' + str(period)) 
    print('Volatility: ' + str(volatility)) 
    print(loss)
    print(profit) 

    #continue here

'''
#visualising 
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(df['Close'], color='b') 
plt.plot(df['EMA10'], color='r')
plt.plot(df['EMA30'], color='g')

plt.xlabel('Date') 
plt.ylabel('Price in $') 
plt.show() '''