''' UNDERSTANDING AND BACKTESTING MOVING AVERAGES STRATEGY 
This script contains an exploration to using moving averages (fast and slow signals crossover) as trading strategy. 
Then, it uses backtrader as a tool to backtest such strategy, calculating the returns over a two year period with an user-decided initial investment amount
'''

#pip3 install yfinance pandas numpy seaborn matplotlib backtrader 
#or 
#pip install yfinance pandas numpy seaborn matplotlib backtrader 
import yfinance as yf 
import pandas as pd 
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches 
import backtrader as bt
import datetime
from datetime import date

usr_ticker = input("Ticker: ") #increase userability to allow for interaction 
usr_fast = input("Fast: ") #userability to decide on fast signal 
usr_slow = input("Slow: ") #userability to decide on slow signal 
usr_cash = input("Starting Cash (£): ")

#to feed the strategy into Cerebro (backtesting engine of backtrader), we must first instantiate a strategy object 
#instantiating a simple moving avg object (SMA)
class sma_cross(bt.Strategy): 
    #create a list of parameters which will become configurable for the strategy (in this case, a MA20 and MA50 crossover strategy) 
    params = dict( 
        pfast = int(usr_fast),
        pslow= int(usr_slow)
    )

    #instantiate strategies to bt.Strategy 
    def __init__(self): 
        sma1 = bt.ind.SMA(period=self.p.pfast) #fast signal 
        sma2 = bt.ind.SMA(period=self.p.pslow) #slow signal 
        self.crossover = bt.ind.CrossOver(sma1, sma2) #indicating the crossover (when we want to buy/sell) 

    def next(self): 
        if not self.position: #not in the market (doesn't yet have a position)  
            if self.crossover > 0: #if fast crosses 50 
                self.buy() #enter long 
        
        elif self.crossover < 0: #if slow crossos slow 
            self.close() #close long position 

class moving_avg(): #creating another object to further manually exploring MA strategies and backtest our 'sma-cross' strategy 
    def backtest(self, usr_ticker, starting_cash): #backtesting function
        #backtest(usr_ticker = str, strating_cash = int) 
        cerebro = bt.Cerebro() #instantiate the backtesting enginer cerebro from backtrader 
        cerebro.broker.set_cash(starting_cash) #assign a starting cash value based on user input 
        print('Portfolio Starting Value: %2f' % starting_cash) 
        data = bt.feeds.YahooFinanceData(dataname=usr_ticker, fromdate=datetime.datetime(2018, 3, 15), todate = date.today()) #feeding data into cerebro from YF
        cerebro.adddata(data) #feed data 
        cerebro.addstrategy(sma_cross) #add strategy 

        cerebro.run() #run cerebro 
        print('Portfolio Terminating Value: %2f' % cerebro.broker.getvalue()) 
        terminating_cash = cerebro.broker.getvalue() #terminating cash position 
        portfolio_returns = ((terminating_cash - starting_cash) / starting_cash) * 100 #calculating % returns if strategy is used 
        print('Portfolio Returns: %2f' % portfolio_returns)
        cerebro.plot() #show graphical intepretation of strategy 

    #the functions below are optional: just purely for the purpose of understanding the mechanisms of MA strategies 
    def get_data(self, usr_ticker): 
        ticker = usr_ticker #declaring ticker 
        get = yf.Ticker(ticker) #get historical data using YFinance 
        self.data = get.history(start='2018-01-01', end=pd.datetime.now()) #declaring historical data 

    def returns(self): 
        self.data['Daily Returns'] = np.log(self.data['Close']) - np.log(self.data['Close'].shift(1)) #plotting returns for better understanding  
    
    def generate_ma(self, fast, slow): 
        self.fast = fast #declaring fast
        self.slow = slow #declaring slow
        self.data['MA'+str(fast)] = self.data['Close'].rolling(str(fast)+'D').mean() #generating MAfast data 
        self.data['MA'+str(slow)] = self.data['Close'].rolling(str(slow)+'D').mean() #generating MAslow data
        self.data['MA'+str(fast)+'backward'] = self.data['MA'+str(fast)].shift(1) #generating lagged data for daily comparison 
        self.data['MA'+str(slow)+'backward'] = self.data['MA'+str(slow)].shift(1) #generating lagged data for daily comparison 
        self.data = self.data.dropna() #some MA data will return NaN, drop to avoid future error 
        self.data = self.data.reset_index(inplace=False) 
    
    def signal(self): #signalling a buy (1), sell (-1), or hold (0) 
        self.data['Buy/Sell'] = [1 if (self.data.loc[i,'MA'+str(self.fast)] > self.data.loc[i, 'MA'+str(self.slow)]) & (self.data.loc[i,'MA'+str(self.fast)+'backward'] < self.data.loc[i, 'MA'+str(self.slow)+'backward']) else -1 if (self.data.loc[i,'MA'+str(self.fast)] < self.data.loc[i, 'MA'+str(self.slow)]) & (self.data.loc[i,'MA'+str(self.fast)+'backward'] > self.data.loc[i, 'MA'+str(self.slow)+'backward'])  else 0 for i in self.data.index]
        #pseudocode: Signal buy if fast signal exceeds slow signal for today (t), given that fast signal did not exceed slow signal for t-1 
        #pseudocode: Signal sell if slow signal exceeds fast signal for today (t), given than slow signal did not exceed fast signal for t-1 
        #pseudocode: Signal hold if else
        print(self.data)

        sell_buy_list = self.data['Buy/Sell'].values.tolist()
        sell_freq = sell_buy_list.count(-1) #count all sell signals in time frame 
        buy_freq = sell_buy_list.count(1) #count all buy signals in time frame 

        print('-'*80)
        print('SIGNAL SUMMARY')
        print('Ticker:' + usr_ticker)
        print('Fast: ' + usr_fast) 
        print('Slow: ' + usr_slow)
        print('Total Buy Signals since 2018: ' + str(buy_freq)) 
        print('Total Sell Signals since 2018: ' + str(sell_freq)) 
        print('-'*80) 
        print('BACKTEST SUMMARY')
    

#instantiate object and call functions
strat = moving_avg() 
strat.get_data(usr_ticker) 
strat.returns()
strat.generate_ma(usr_fast, usr_slow)
strat.signal() 
strat.backtest(usr_ticker, int(usr_cash)) 