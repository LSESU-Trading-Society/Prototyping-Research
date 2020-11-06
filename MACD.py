import matplotlib.pyplot as plt
import datetime
import yfinance as yf

ticker = 'AAPL'

start_time = datetime.datetime(2020, 1, 1)
end_time = datetime.datetime(2020, 10, 10)

query = yf.Ticker(ticker)

df = query.history(start=start_time,end=end_time)
df = df.reset_index()

df = df[['Date', 'Close']]
df.columns = ['x', 'y']
plt.plot(df.x, df.y, label='GOOGL')
plt.show()

exp_12 = df.y.ewm(span=12, adjust=False).mean()
exp_26 = df.y.ewm(span=26, adjust=False).mean()

macd = exp_12 - exp_26

exp3 = macd.ewm(span=9, adjust=False).mean()

plt.plot(df.x, macd, label='MACD', color='#EBD2BE')
plt.plot(df.x, exp3, label='Signal Line', color = '#E5A4CB')
plt.legend(loc='upper left')
plt.show()

