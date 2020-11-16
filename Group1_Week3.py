import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import date,datetime,timedelta
from statsmodels.tsa.stattools import adfuller

# Importing the data

ticker1 = 'PEP' #Pepsi
# ticker2 = 'KO' #Coca-Cola
first_day = datetime(2017, 1, 1)
last_day = date.today()

print(last_day)

globals()[ticker1] = yf.Ticker(ticker1).history(start=first_day, end=last_day)
# globals()[ticker2] = yf.Ticker(ticker2).history(start=first_day, end=last_day)

PEP.reset_index(inplace=True)
# KO.reset_index(inplace=True)
# pd.set_option('display.max_rows', 1000)

# Functions: (each function adds the relevant indicator(s) X to your data with the name X_param2_param3_param4_... and then returns the initial data with the new column(s))

def SMA(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Simple Moving Average

    tickerData['SMA' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData[columnToUse].rolling(time_window).mean()

    return tickerData

def MNTI(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Momentum Indicator

    tickerData['MNTI' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData[columnToUse].diff(time_window)

    return tickerData

def RSI(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Relative Strength
    tickerData['Diff'] = tickerData[columnToUse].diff(1)
    tickerData['PosReturn'] = 0
    tickerData['NegReturn'] = 0

    tickerData['PosReturn'][tickerData['Diff']>0] = tickerData['Diff']
    tickerData['NegReturn'][tickerData['Diff']<0] = -tickerData['Diff']

    tickerData['AveragePosReturn'] = tickerData['PosReturn'].rolling(window = time_window,min_periods = time_window).mean()
    tickerData['AverageNegReturn'] = tickerData['NegReturn'].rolling(window = time_window,min_periods = time_window).mean()

    tickerData['RSI' + '_' + str(columnToUse) + '_' + str(time_window)] = 100 - 100/(1 + abs(tickerData['AveragePosReturn']/tickerData['AverageNegReturn']))
    tickerData.drop(['Diff','PosReturn','NegReturn','AveragePosReturn','AverageNegReturn'], axis = 1, inplace = True)
    return tickerData

def BB(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Bollinger Band
    tickerData['MBB' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData[columnToUse].rolling(time_window).mean()
    tickerData['LBB' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData['MBB' + '_' + str(columnToUse) + '_' + str(time_window)] - (2 * tickerData[columnToUse].rolling(time_window).std())
    tickerData['UBB' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData['MBB' + '_' + str(columnToUse) + '_' + str(time_window)] + (2 * tickerData[columnToUse].rolling(time_window).std())

    return tickerData

def EMA(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Exponential Moving Average
    tickerData['EMA' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData[columnToUse].ewm(span=time_window).mean()
    return tickerData

def MACD(tickerData: pd.DataFrame, columnToUse: str) -> pd.DataFrame: #Moving Average Convergence Divergence
    tickerData['exp_12'] = tickerData[columnToUse].ewm(span=12).mean()
    tickerData['exp_26'] = tickerData[columnToUse].ewm(span=26).mean()

    tickerData['MACD' + '_' + str(columnToUse)] = tickerData['exp_12'] - tickerData['exp_26']

    tickerData['MACD_signal' + '_' + str(columnToUse)] = tickerData['MACD' + '_' + str(columnToUse)].ewm(span=9).mean()
    tickerData.drop(['exp_12','exp_26'], axis = 1, inplace = True)
    return tickerData


# Testing stuff

BB(PEP,'Close',20)

Strat1 = pd.DataFrame({'Date' : PEP.Date}) 
Strat1['Entry1'] = np.where(PEP['Close'] > PEP['UBB_Close_20'], -1, np.where(PEP['Close'] < PEP['LBB_Close_20'], 1, 0)) # -1 - Sell, 1 - Buy
Strat1['Exit1'] = -Strat1['Entry1'].shift(1)
# Strat1['Exit'] = Strat1['Exit1'] and not entry true then close all pos (to be coded)
Strat1['Cumm'] = Strat1['Entry1'].cumsum() + Strat1['Exit1'].cumsum()
Strat1['Cumm'] = Strat1['Cumm'].shift(1)
Strat1['Daily_Change'] = PEP['Close'].diff(1)
Strat1['Daily_Return'] = Strat1['Daily_Change'] * Strat1['Cumm']
Strat1['Close'] = PEP['Close']

print(Strat1)
print(Strat1['Daily_Return'].sum())


#Plotting stuff


plt.plot(PEP.Date,Strat1.Cumm, label = 'Exposure')
plt.show()


plt.xlabel("Days")
plt.ylabel("Price")

plt.plot(PEP.Date,PEP['Close'], label = "Price")
plt.plot(PEP.Date,PEP['MBB_Close_20'], label = "20-day mean")
plt.plot(PEP.Date,PEP['UBB_Close_20'], label = "Upper")
plt.plot(PEP.Date,PEP['LBB_Close_20'], label = "Lower")
plt.plot(PEP.Date,Strat1['Entry1'], label = 'Entry')
plt.plot(PEP.Date,Strat1['Exit1'], label = 'Exit')
plt.legend(loc = 'upper left')
plt.show()