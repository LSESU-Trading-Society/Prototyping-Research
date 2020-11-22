import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import date,datetime,timedelta
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm

# Importing the data

ticker1 = 'PEP' #Pepsi
ticker2 = 'KO' #Coca-Cola
first_day = datetime(2020, 5, 1)
last_day = date.today()

PEP = yf.Ticker(ticker1).history(start=first_day, end=last_day)
KO = yf.Ticker(ticker2).history(start=first_day, end=last_day)

# PEP.reset_index(inplace=True)
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


# Combining PEP and KO

PEPKO = pd.DataFrame(index = PEP.index)

PEPKO['Pepsi'] = PEP.Close
PEPKO['Coca_Cola'] = KO.Close

# regression = sm.OLS(np.log(PEPKO['Pepsi']), np.log(PEPKO['Coca_Cola'])).fit()
regression = sm.OLS(PEPKO['Pepsi'], PEPKO['Coca_Cola']).fit()
beta1 = regression.params[0]
print(beta1)
spread = pd.DataFrame(index = PEPKO.index)
# spread['spread'] = np.log(PEPKO['Pepsi']) - beta1*np.log(PEPKO['Coca_Cola'])
spread['spread'] = np.log(PEPKO['Coca_Cola']) - beta1*np.log(PEPKO['Pepsi'])
# spread['spread'] = PEPKO['Pepsi'] - beta*PEPKO['Coca_Cola']

# plt.scatter(np.log(PEPKO.Pepsi),np.log(PEPKO.Coca_Cola))
plt.plot(spread.index,spread.spread)
plt.axhline(spread.spread.mean(), linestyle = '--')
plt.show()


result = adfuller(spread['spread'])
# print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
# for key, value in result[4].items():
    # print('Critial Values:')
    # print(f'{key}, {value}')
# print(result)
