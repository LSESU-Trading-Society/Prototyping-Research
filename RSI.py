import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import pandas_datareader as web
import yfinance as yahoo_finance
from pandas import DataFrame


def computeRSI(tickerData: DataFrame, columnToUse: str, time_window: int) -> DataFrame:
    tickerData['Diff'] = tickerData[columnToUse].diff(1).dropna()
    tickerData['IsPosReturn'] = tickerData['Diff'] > 0

    tickerData['AveragePosReturn'] = [tickerData['Diff'].rolling(time_window).ewm() if tickerData.loc[i, 'isPosReturn'] else 0 for i in tickerData.index]
    tickerData['AverageNegReturn'] = [tickerData['Diff'].rolling(time_window).ewm() if tickerData.loc[i, 'isPosReturn'] else 0 for i in tickerData.index] ## Not RIGHT!!!

    tickerData['RSI' + time_window] = 100 - 100/(1 + abs(tickerData['AveragePosReturn']/tickerData['AverageNegReturn']))

    return tickerData


ticker = 'GOOGL'

start_time = datetime.datetime(2020, 10, 1)
end_time = datetime.datetime.now().date().isoformat()         # today

connected = False
while not connected:
    try:
        ticker_df = web.get_data_yahoo(ticker, start=start_time, end=end_time)
        connected = True
        print('connected to yahoo')
    except Exception as e:
        print("type error: " + str(e))
        time.sleep( 5 )
        pass

ticker_df = ticker_df.reset_index()
print(ticker_df.head(5))

ticker_df = computeRSI(ticker_df, 'Adj Close', 14)

print(ticker_df.head())