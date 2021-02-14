import yfinance as yf
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
from datetime import date,datetime,timedelta

# Importing the data

ticker1 = 'AAPL' #Gamestop
first_day = datetime(2018, 1, 1)
last_day = datetime(2021, 2, 2)

data = yf.Ticker(ticker1).history(interval = '1d', start=first_day, end=last_day)

data.reset_index(inplace=True)

pd.set_option('display.max_rows', 1000)

def SMA(tickerData: pd.DataFrame, columnToUse: str, time_window: int) -> pd.DataFrame: #Simple Moving Average

    tickerData['SMA' + '_' + str(columnToUse) + '_' + str(time_window)] = tickerData[columnToUse].rolling(time_window).mean()

    return tickerData

SMA(data, "Close", 50)
SMA(data, "Close", 200)



#Basic SMA Strategy to illustrate the use of SL/TP
def SMA_signal(tickerData: pd.DataFrame, period: int, short_term_SMA: str, long_term_SMA: str):
    if (tickerData[short_term_SMA][period] > tickerData[long_term_SMA][period]) and (tickerData[short_term_SMA][period-1] < tickerData[long_term_SMA][period-1]):
        return 1
    elif (tickerData[short_term_SMA][period] < tickerData[long_term_SMA][period]) and (tickerData[short_term_SMA][period-1] > tickerData[long_term_SMA][period-1]):
        return -1
    else:
        return 0

stoploss_level = 0.05
takeprofit_level = 0.05

position_state = 0 #this variable is to ensure we have only one position at a time
Portfolio = pd.DataFrame()
Portfolio['Price'] = data.Close
Portfolio['Cash'] = 0
Portfolio['Holdings'] = 0
Portfolio['Position'] = 0
Portfolio['Stoploss'] = 0
Portfolio['Takeprofit'] = 0
Portfolio['Total'] = 0
Cash = 100000

Portfolio.Cash[0] = Cash
Portfolio.Total[0] = Cash


for period in data.index: #go through each period

    try:#this try/except KeyError statement helps skip the loop in which we have negative indexing 
        #(ie. the first loop period is 0 so period-1 is -1 which cannot be used as an index) 
         
            #This if statement checks if the signal is activated and buys if we don't already have an open position
            if (position_state == 0) and (SMA_signal(data, period, "SMA_Close_50", "SMA_Close_200") == 1):
                position_state = 1
                Portfolio.Holdings[period] = Portfolio.Cash[period-1]//Portfolio.Price[period]
                Portfolio.Cash[period] = Portfolio.Cash[period-1] - Portfolio.Holdings[period] * Portfolio.Price[period]
                Portfolio.Position[period] += Portfolio.Holdings[period] * Portfolio.Price[period]
                Portfolio.Stoploss[period] = Portfolio.Position[period] * (1-stoploss_level)
                Portfolio.Takeprofit[period] = Portfolio.Position[period] * (1+takeprofit_level)
                Portfolio.Total[period] = Portfolio.Cash[period] + Portfolio.Position[period]

            elif (position_state == 0) and (SMA_signal(data, period, "SMA_Close_50", "SMA_Close_200") == -1):
                position_state = -1
                Portfolio.Holdings[period] = -(Portfolio.Cash[period-1]//Portfolio.Price[period])
                Portfolio.Cash[period] = Portfolio.Cash[period-1] - Portfolio.Holdings[period] * Portfolio.Price[period]
                Portfolio.Position[period] += Portfolio.Holdings[period] * Portfolio.Price[period]
                Portfolio.Stoploss[period] = Portfolio.Position[period] * (1+stoploss_level)
                Portfolio.Takeprofit[period] = Portfolio.Position[period] * (1-takeprofit_level)
                Portfolio.Total[period] = Portfolio.Cash[period] + Portfolio.Position[period]

            #This elif statement checks if a sell signal is actived and sells if we already bought beforehand (we could short-sell too but it is kept simple since the strategy is not the main goal here) OR if one of the SL/TP levels have been crossed
            elif (position_state == 1) and ((SMA_signal(data, period, "SMA_Close_50", "SMA_Close_200") == -1) or (Portfolio.Position[period-1]<Portfolio.Stoploss[period-1]) or (Portfolio.Position[period-1]>Portfolio.Takeprofit[period-1])):
                position_state = 0
                Portfolio.Holdings[period] = 0
                Portfolio.Cash[period] = Portfolio.Cash[period-1] + (Portfolio.Holdings[period-1] * Portfolio.Price[period])
                Portfolio.Position[period] = 0
                Portfolio.Stoploss[period] = 0
                Portfolio.Takeprofit[period] = 0
                Portfolio.Total[period] = Portfolio.Cash[period] + Portfolio.Position[period]
            
            elif (position_state == -1) and ((SMA_signal(data, period, "SMA_Close_50", "SMA_Close_200") == 1) or (Portfolio.Position[period-1]<Portfolio.Stoploss[period-1]) or (Portfolio.Position[period-1]>Portfolio.Takeprofit[period-1])):
                position_state = 0
                Portfolio.Holdings[period] = 0
                Portfolio.Cash[period] = Portfolio.Cash[period-1] + (Portfolio.Holdings[period-1] * Portfolio.Price[period])
                Portfolio.Position[period] = 0
                Portfolio.Stoploss[period] = 0
                Portfolio.Takeprofit[period] = 0
                Portfolio.Total[period] = Portfolio.Cash[period] + Portfolio.Position[period]

            #This else statement is just what happens if nothing is activated, it just updates our position's value
            else:
                Portfolio.Holdings[period] = Portfolio.Holdings[period-1]
                Portfolio.Cash[period] = Portfolio.Cash[period-1]
                Portfolio.Position[period] = Portfolio.Holdings[period] * Portfolio.Price[period]
                Portfolio.Stoploss[period] = Portfolio.Stoploss[period-1]
                Portfolio.Takeprofit[period] = Portfolio.Takeprofit[period-1]
                Portfolio.Total[period] = Portfolio.Cash[period] + Portfolio.Position[period]
    except KeyError:
        pass
            
print(Portfolio)

plt.plot(Portfolio.index,Portfolio.Total, label = "Total")
plt.plot(Portfolio.index[Portfolio.Stoploss!=0],abs(Portfolio.Stoploss[Portfolio.Stoploss!=0]))
plt.plot(Portfolio.index[Portfolio.Takeprofit!=0],abs(Portfolio.Takeprofit[Portfolio.Takeprofit!=0]))
plt.show()
