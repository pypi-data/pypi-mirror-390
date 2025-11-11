Practical no 4
Aim: Working with stationary and non stationary timeseries


Stationary Time Series

# load time series data
from pandas import read_csv
from matplotlib import pyplot
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-total-female-births.csv', header=0, index_col=0, parse_dates=True,
squeeze=True)
series.plot()
pyplot.show()



*********



Non-Stationary Time Series


# load time series data
from pandas import read_csv
from matplotlib import pyplot
series = read_csv('/content/drive/MyDrive/MScDS TSA/AirPassengers.csv', header=0, index_col=0, parse_dates=True,
squeeze=True)
series.plot()
pyplot.show()



**********



Summary Statistics: You can review the summary statistics for your data for seasons or random partitions and check for obvious or significant differences

# plot a histogram of a time series
from pandas import read_csv
from matplotlib import pyplot
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-total-female-births.csv', header=0, index_col=0, parse_dates=True,
squeeze=True)
series.hist()
pyplot.show()



***********


we can split the time series into two contiguous sequences. We can then calculate the mean and variance of each group of numbers and compare the values.

PART1ST

# calculate statistics of partitioned time series data
from pandas import read_csv
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-total-female-births.csv', header=0, index_col=0, parse_dates=True,squeeze=True)

X = series.values
split = int(len(X) / 2)
X1, X2 = X[0:split], X[split:]
mean1, mean2 = X1.mean(), X2.mean()
var1, var2 = X1.var(), X2.var()
print('mean1=%f, mean2=%f' % (mean1, mean2))
print('variance1=%f, variance2=%f' % (var1, var2))


PART 2ND

# calculate statistics of partitioned time series data
from pandas import read_csv
series = read_csv('/content/drive/MyDrive/MScDS TSA/AirPassengers.csv', header=0, index_col=0, parse_dates=True,
squeeze=True)
X = series.values
split = int(len(X) / 2)
X1, X2 = X[0:split], X[split:]
mean1, mean2 = X1.mean(), X2.mean()
var1, var2 = X1.var(), X2.var()
print('mean1=%f, mean2=%f' % (mean1, mean2))
print('variance1=%f, variance2=%f' % (var1, var2))



***********


C] Statistical Tests: You can use statistical tests to check if the expectations of stationarity are met or have been violated

# calculate stationarity test of time series data
from pandas import read_csv
from statsmodels.tsa.stattools import adfuller
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-total-female-births.csv', header=0, index_col=0, parse_dates=True,
squeeze=True)
X = series.values
result = adfuller(X)
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
  print('\t%s: %.3f' % (key, value))


**************


#Importing the libraries:

from statsmodels.tsa.stattools import adfuller
import pandas as pd
import numpy as np

#Reading the airline-passengers data

data = pd.read_csv('/content/drive/MyDrive/MScDS TSA/AirPassengers.csv', index_col='Month')

#Checking for some values of the data.

data.head()


************


#Plotting the data.

data.plot(figsize=(14,8), title='data series')

#Taking out the passengers number as a series.

series = data['#Passengers'].values
#print(series)


***********



#Performing the ADF test on the series:

# ADF Test
result = adfuller(series, autolag='AIC')
#Extracting the values from the results:

print('ADF Statistic: %f' % result[0])

print('p-value: %f' % result[1])

print('Critical Values:')

for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))
if result[0] < result[4]["5%"]:
    print ("Reject Ho - Time Series is Stationary")
else:
    print ("Failed to Reject Ho - Time Series is Non-Stationary")




The test statistic is positive, meaning we are much less likely to reject the null hypothesis (it looks non-stationary). Comparing the test statistic to the critical values, it looks like we would have to fail to reject the null hypothesis that the time series is non-stationary and does have time-dependent structure.


#Kwiatkowski Phillips Schmidt Shin (KPSS) test:

#Importing the libraries:

from statsmodels.tsa.stattools import kpss
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

result_kpss_ct=kpss(series,regression="ct")
print('Test Statistic: %f' %result_kpss_ct[0])
print('p-value: %f' %result_kpss_ct[1])
print('Critical values:')
for key, value in result_kpss_ct[3].items():
     print('\t%s: %.3f' %(key, value))



**********

#Loading the data.

path = '/content/daily-min-temperatures.csv'
data = pd.read_csv(path, index_col='Date')

#Checking for some head values of the data:

data.head()



**********

#Plotting the data.

data.plot(figsize=(14,8), title='temperature data series')


**********


#Extracting temperature in a series.

series = data['Temp'].values
series

***********


#Performing ADF test.

result = adfuller(series, autolag='AIC')

#Checking the results:

print('ADF Statistic: %f' % result[0])

print('p-value: %f' % result[1])

print('Critical Values:')

for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))
if result[0] > result[4]["5%"]:
    print ("Reject Ho - Time Series is Stationary")
else:
    print ("Failed to Reject Ho - Time Series is Stationary")

