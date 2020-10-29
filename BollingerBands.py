import pandas as pd
import yfinance as yf
import yahoofinancials
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import date

from datetime import datetime
from scipy.stats import kurtosistest

ticker = 'TSLA' #QUIDEL
query = yf.Ticker(ticker) #instantiating Ticker object, feeding it our ticker
df = query.history(start=datetime(2020, 1, 1), end=datetime(2020,10,10))  #querying data, datetime() formats our dates into readable time series date

print(df.head())

periods = 21
sd_mult = 2.5

df['MA21'] = df['Close'].ewm(periods).mean()
df['Upper'] = df['MA21'] + sd_mult*df['Close'].ewm(periods).std()
df['Lower'] = df['MA21'] - sd_mult*df['Close'].ewm(periods).std()
df['Daily Return'] = df['Close'].pct_change()
#
df['HitUpper'] = df['High'] > df['Upper'].shift(1)
df['HitLower'] = df['Low'] < df['Lower'].shift(1)

plt.figure(figsize = (12,6))
plt.plot(df['Close'], label="Price")
plt.plot(df['MA21'], label="21-Day EMA")
plt.plot(df['Upper'], label="Upper")
plt.plot(df['Lower'], label="Lower")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()

##TODO: Try and write the code to analyse by what percentage we move above and/or below the band on average after generating a "signal"

#making an edit













