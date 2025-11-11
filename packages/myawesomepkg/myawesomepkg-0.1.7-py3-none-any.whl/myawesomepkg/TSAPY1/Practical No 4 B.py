PRCTICAL 4 B



def test_stationarity(dataFrame, var):
  dataFrame['rollMean']=dataFrame[var].rolling(window=12).mean()
  dataFrame['rollStd']=dataFrame[var].rolling(window=12).std()

  from statsmodels.tsa.stattools import adfuller
  import seaborn as sns
  adfTest = adfuller(dataFrame[var], autolag='AIC')
  stats=pd.Series(adfTest[0:4],index=['Test Statistic','p-value', '#lags used', 'number of observations used'])
  print(stats)

  for key, value in adfTest[4].items():
    print('\t%s: %.3f' % (key, value))

  sns.lineplot(data=dataFrame, x=dataFrame.index, y=var)
  sns.lineplot(data=dataFrame, x=dataFrame.index, y='rollMean')
  sns.lineplot(data=dataFrame, x=dataFrame.index, y='rollStd')


********



import pandas as pd
import numpy as np

#Reading the airline-passengers data

data = pd.read_csv('/content/drive/MyDrive/MScDS TSA/AirPassengers.csv', index_col='Month')

#Checking for some values of the data.

data.head()



************



air_df=data[['Passengers']]
air_df.head()




**********

air_df['shift']=air_df.Passengers.shift()
air_df['shiftDiff']=air_df.Passengers - air_df['shift']
air_df.head()


**********

test_stationarity(air_df.dropna(),'shiftDiff')


***********

log_df=air_df[['Passengers']]
log_df['log']=np.log(log_df['Passengers'])
log_df.head()


************

test_stationarity(log_df,'log')



sqrt_df=air_df[['Passengers']]
sqrt_df['sqrt']=np.sqrt(air_df['Passengers'])
sqrt_df.head()


********

test_stationarity(sqrt_df,'sqrt')


***********

cbrt_df=air_df[['Passengers']]
cbrt_df['cbrt']=np.cbrt(air_df['Passengers'])
cbrt_df.head()

***********

test_stationarity(cbrt_df,'cbrt')




************


log_df2=log_df[['Passengers','log']]
log_df2['log_sqrt']=np.sqrt(log_df['log'])
log_df2.head()

**********


test_stationarity(log_df2,'log_sqrt')



********


log_df2=log_df[['Passengers','log']]
log_df2['log_sqrt']=np.sqrt(log_df['log'])
log_df2['logShiftDiff']=log_df2['log_sqrt']-log_df2['log_sqrt'].shift()
log_df2.head()



*********


test_stationarity(log_df2.dropna(),'logShiftDiff')

*************88










