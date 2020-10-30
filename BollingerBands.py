import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

ticker = 'TSLA' #QUIDEL
query = yf.Ticker(ticker) #instantiating Ticker object, feeding it our ticker
df = query.history(start=datetime(2020, 1, 1), end=datetime(2020,10,10))  #querying data, datetime() formats our dates into readable time series date


periods = 21
sd_mult = 1

df['MA21'] = df['Close'].ewm(periods).mean()
df['Upper'] = df['MA21'] + sd_mult*df['Close'].ewm(periods).std()
df['Lower'] = df['MA21'] - sd_mult*df['Close'].ewm(periods).std()
df['Daily Return'] = df['Close'].pct_change()
#
df['HitUpper'] = df['High'] > df['Upper'].shift(1)
df['HitLower'] = df['Low'] < df['Lower'].shift(1)

df['MaxUpper'] = 100*(df['High'] - df['Upper'].shift(1))/df['Upper'].shift(1)
df.MaxUpper[df['MaxUpper']< 0]=np.NaN
print(df['MaxUpper'].mean())
print(df['MaxUpper'].max())

df['MaxLower'] = 100*(df['Low'] - df['Lower'].shift(1))/df['Lower'].shift(1)
df.MaxLower[df['MaxLower']> 0]=np.NaN
print(df['MaxLower'].mean())
print(df['MaxLower'].min())

plt.figure(figsize = (12,6))
plt.plot(df['Close'], label="Price")
plt.plot(df['MA21'], label="21-Day EMA")
plt.plot(df['Upper'], label="Upper")
plt.plot(df['Lower'], label="Lower")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()
