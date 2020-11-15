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

#----------QUERYING AND CLEANING DATA ---------# 

t_data = yf.download("DGOC.L AR", start = datetime.datetime(2020,5,1), end = date.today())
close_price = t_data['Close']
close_price = close_price.dropna() 
print(close_price) 

#-------- BETA HEDING RATIO AND SPREAD -------- #
model = sm.OLS(close_price['DGOC.L'], close_price['AR']).fit() 
beta = model.params[0] 
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
plt.show() 

#scatterplot of prices
sns.set() 
plt.figure(figsize=(10,10)) 
plt.scatter(close_price['DGOC.L'], close_price['AR'], color='b') 
plt.title('Corresponding DGOC.L and AR prices')
plt.show() 

#estimating mean reverting properties 
sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot((close_price['DGOC.L'] - close_price['AR']), color='b') 
plt.axhline((close_price['DGOC.L'] - close_price['AR']).mean(), linestyle='--', color='r')
plt.title('Price and Mean Reversion')
plt.show() 

sns.set() 
plt.figure(figsize=(10,10)) 
plt.plot(close_price['Spread'], color='r') 
plt.axhline(close_price['Spread'].mean(), linestyle = '--', color='g') 
plt.title('Spread')
plt.show() 

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


#isZUpper -> sell DGOC, buy AR 
#isZLower -> sell AR, buy DGOC 

# ------ BACKTESTING ------- # 
#pseudocode here: (working solely with z = 1 -> sell DGOC and buy AR (considered for beta hedge ratio)) 
#when z = 1 lower -> buy DGOC and sell PMO (adjusted for beta hedge) 
#long assumptions: no commission 
#short assumptions: short selling, no commission 
#further development notes: commission? stop losses? put option instead of short selling? 



