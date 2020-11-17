'''Notes on instruments: 
- equities - noting the Market rally on monday 
    LSE -> PMO/BP correlated 
    Appalachian Basin: AR / DGOC.L / EQT / COG (basket) 
- commodities: Brent Crude / Opec Basket Futures + Opec Basket / Mars US 
''' 
#-----------IMPORT LIBRARIES-----------#
import yfinance as yf 
import matplotlib.pyplot as plt 
import seaborn as sns 
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.stattools import adfuller 
import scipy.stats as stats
import statsmodels.api as sm
import datetime 
from datetime import date 
import numpy as np 
import pandas as pd 

#----------QUERYING AND CLEANING DATA ---------# 

t_data = yf.download("DGOC.L AR", start = datetime.datetime(2020,5,1), end = date.today())
close_price = t_data['Close']
close_price = close_price.dropna() 
print(close_price) 

#-------- BETA HEDING RATIO AND SPREAD -------- #
model = sm.OLS(close_price['DGOC.L'], close_price['AR']).fit() 
beta = model.params[0] 
print(beta)
epsilon = model.resid 

close_price['Spread'] = np.log(close_price['DGOC.L']) - beta * np.log(close_price['AR'])


#------- INITIAL VISUALISATION ------# 
#price movement
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(close_price['DGOC.L'], color='b') 
plt.plot(close_price['AR'] * 20, color='orange') 
plt.xlabel('Date') 
plt.ylabel('Close Price in Exchange Currency') 
plt.title('DGOC.L vs AR (scaled)') 
#plt.show() 

#scatterplot of prices
sns.set() 
plt.figure(figsize=(10,10)) 
plt.scatter(close_price['DGOC.L'], close_price['AR'], color='b') 
plt.title('Corresponding DGOC.L and AR prices')
#plt.show() 

#estimating mean reverting properties 
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot((close_price['DGOC.L'] - close_price['AR']), color='b') 
plt.axhline((close_price['DGOC.L'] - close_price['AR']).mean(), linestyle='--', color='r')
plt.title('Price and Mean Reversion')
#plt.show() 

sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(close_price['Spread'], color='r') 
plt.axhline(close_price['Spread'].mean(), linestyle = '--', color='g') 
plt.title('Spread')
#plt.show() 

# -------- STATIONARITY SUMMARY ------ #
print('STATIONARITY TEST SUMMARY') 
print('-'*30)
print('Beta Hedging Ratio: ' + str(beta)) 

print('P_Value with ADF on Residual: ') 
print(sm.tsa.stattools.adfuller(epsilon)[1])

print('P_Value of Prices with ADF (Dollar Neutral): ')
print(sm.tsa.stattools.adfuller(np.log(close_price['DGOC.L']) - np.log(close_price['AR']))[1])

print('P-Value of Spread with ADF (Stationarity): ')
adf_result = sm.tsa.stattools.adfuller(close_price['Spread']) 
print('%f' % adf_result[1])

rolling_window = 5 

close_price['Spread Mu'] = close_price['Spread'].rolling(5).mean() 
close_price['Spread Sigma'] = close_price['Spread'].rolling(5).std(ddof=1) 
close_price = close_price.dropna() 
close_price['SpreadZ-Score'] = (close_price['Spread'] - close_price['Spread Mu'] / close_price['Spread Sigma'])

threshold_1 = 1 #changeable 
threshold_2 = 1.5

close_price['Z_Level1'] = threshold_1 * close_price['Spread Sigma']
close_price['Z_Level2'] = threshold_2 * close_price['Spread Sigma']


#condition this to first day of series 
close_price['isZUpper'+str(threshold_1)] = close_price['SpreadZ-Score'] >= close_price['Z_Level1']
close_price['isZUpper'+str(threshold_2)] = close_price['SpreadZ-Score'] >= close_price['Z_Level2']
close_price['isZLower'+str(threshold_1)] = close_price['SpreadZ-Score'] <= close_price['Z_Level1']
close_price['isZLower'+str(threshold_2)] = close_price['SpreadZ-Score'] <= close_price['Z_Level2']

close_price=close_price.reset_index() 
print(close_price)



# ------ BACKTESTING ------- # 
#pseudocode here: (working solely with z = 1 -> sell DGOC and buy AR (considered for beta hedge ratio)) 
#when z = 1 lower -> buy DGOC and sell PMO (adjusted for beta hedge) 
#long assumptions: no commission 
#short assumptions: short selling, no commission 
#further development notes: commission? stop losses? put option instead of short selling? 

#we construct a portfolio record of all transactions based on signals 
portfolio = pd.DataFrame() 
asset_name = [] 
date_transacted = []
trans_type = [] 
price = [] 
no_of_shares = []
cash_position = []

#defining parameters: #of shares, buy/sell more, sell type (FIFO/WA) 
isBuyMore = False 
sell_type = 'FIFO' 
share_no = 1 
cash = 10000 
''' Position logic (only buying/selling on the first day of consecutive like signals )
#isZUpper1 
false x
false 
false 
-
True x 
True
-
false x
-
true x
- 
false x
false '''

#isZUpper -> sell DGOC, buy AR 
#isZLower -> sell AR, buy DGOC 

#Approach 1: Buy x share on everyday there is a signal 
#Approach 2: Buy x share on the first day in a series of yes signal
#We're assuming approach 2 first 

#(not finished) we want to assume positions so that dgoc + ar always amounts to max. cash position -> dgoc + 31 ar = cash
#positions on dgoc = 1/(beta+1)  * cash / pps 
#positions on ar = beta/beta+1 * cash / pps 

#assuming fixed positions on all transaction: one share of dgoc, dgoc share * beta shares of ar 

#append cash_position after each transaction 

for i in close_price.index: 
    try:
        #i-1 must be false because we are only buying on the first day, if there are consecutive signals
        if (close_price.loc[i, 'isZUpper1'] == True) & (close_price.loc[i-1, 'isZUpper1'] != True): 
            asset_name.append('DGOC.L') 
            date_transacted.append(close_price.loc[i, 'Date'])  
            trans_type.append('Sell FIFO') 
            price.append(close_price.loc[i, 'DGOC.L']) 
            no_of_shares.append(share_no) #/(beta+1)*cash / close_price.loc[i, 'DGOC.L'])
            cash_position.append(cash + (share_no * close_price.loc[i, 'DGOC.L'])) #/(beta+1)*cash / close_price.loc[i, 'DGOC.L']) 
            cash = (cash + (share_no * close_price.loc[i, 'DGOC.L'])) #cash - (1/(beta+1)*cash / close_price.loc[i, 'DGOC.L']) * close_price.loc[i, 'DGOC.L']
            
            asset_name.append('AR') 
            date_transacted.append(close_price.loc[i, 'Date']) 
            trans_type.append('Buy') 
            price.append(close_price.loc[i, 'AR']) 
            no_of_shares.append(beta * share_no)  #/(beta+1) * cash / close_price.loc[i, 'AR'])
            cash_position.append(cash - beta*share_no * close_price.loc[i, 'AR']) #(beta/(beta+1) * cash / close_price.loc[i, 'AR']) 
            cash = (cash - beta*share_no * close_price.loc[i, 'AR']) #cash + (beta/(beta+1) * cash / close_price.loc[i, 'AR']) * close_price.loc[i, 'AR']

        elif (close_price.loc[i, 'isZLower1'] == True) & (close_price.loc[i-1, 'isZLower1'] != True): 
            asset_name.append('AR') 
            date_transacted.append(close_price.loc[i, 'Date'])  
            trans_type.append('Sell FIFO') 
            price.append(close_price.loc[i, 'AR']) 
            no_of_shares.append(beta*share_no) #/(beta+1) * cash / close_price.loc[i, 'AR'])
            cash_position.append(cash + beta*share_no * close_price.loc[i, 'AR']) #(beta/(beta+1) * cash / close_price.loc[i, 'AR']) 
            cash = (cash + beta*share_no * close_price.loc[i, 'AR']) #cash + (beta/(beta+1) * cash / close_price.loc[i, 'AR']) * close_price.loc[i, 'AR']

            asset_name.append('DGOC.L') 
            date_transacted.append(close_price.loc[i, 'Date']) 
            trans_type.append('Buy') 
            price.append(close_price.loc[i, 'DGOC.L']) 
            no_of_shares.append(share_no) #/(beta+1)*cash / close_price.loc[i, 'DGOC.L'])
            cash_position.append(cash - (share_no * close_price.loc[i, 'DGOC.L'])) #/(beta+1)*cash / close_price.loc[i, 'DGOC.L']) 
            cash = (cash - (share_no * close_price.loc[i, 'DGOC.L'])) #cash - (1/(beta+1)*cash / close_price.loc[i, 'DGOC.L']) * close_price.loc[i, 'DGOC.L']
    except KeyError: 
        pass 

portfolio['Name'] = asset_name 
portfolio['Date'] = date_transacted 
portfolio['Type'] = trans_type 
portfolio['Price per Share'] = price 
portfolio['No of Shares'] = no_of_shares 
portfolio['CurrentCashPosition'] = cash_position
portfolio = portfolio.set_index('Date')
if 'Buy' == portfolio['Type'].iloc[-1]: 
    portfolio = portfolio[:-1]
print(portfolio) 

ending_cash = portfolio['CurrentCashPosition'].iloc[-1]
returns = (ending_cash - cash) / cash * 100

print('STRATEGY SUMMARY') 
print('-'*30) 
print('Security 1: ' + str(close_price.columns[1]))
print('Security 2: ' + str(close_price.columns[2]))
print('Strategy Period: ' + str(close_price.index[-1] - close_price.index[0]))
print('-'*30) 
print('Buy More Volume with Consecutive Signals: ' + str(isBuyMore)) 
print('Sell Order ' + str(sell_type)) 
print('Starting Cash: ' + str(cash)) 
print('Ending Cash: ' + str(ending_cash)) 
print('Returns (%) : ' + str(returns)) 

'''suggested improvements: 
- total portfolio value > fixed share
- Summarise returns 
- Stop losses 
- Buy/sell more? 
- Compare returns with different parameters 
- Other assets (using the same functions/methods) 
''' 