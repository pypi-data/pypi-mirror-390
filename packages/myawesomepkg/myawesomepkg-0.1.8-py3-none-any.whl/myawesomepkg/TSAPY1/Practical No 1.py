Practical No 1: Aim: Handling timeseries data

A. Load and Explore Time Series Data

from pandas import read_csv
series = read_csv('/content/daily-total-female-births.csv', header=0, index_col=0, parse_dates=True)
print(type(series))
print(series.head())

You can use the head() function to peek at the first 5 records

print(series.head(10))


Number of Observations 

print(series.size)


Querying By Time

print(series.loc["1959-01"])


The describe() function creates a 7 number summary of the loaded time series including mean, standard deviation, median, minimum, and maximum of the observations

print(series.describe())



"""B. Data Visualization"""


Minimum Daily Temperatures Dataset

from pandas import read_csv
from matplotlib import pyplot
series = read_csv('daily-min-temperatures.csv', header=0, index_col=0,parse_dates=True)
print(series.head())
series=series.squeeze()
type(series)
print(series.describe())


Line Plot 

series.plot()
pyplot.show()

&&&

series.plot(style='k.')
pyplot.show()

&&&

series.plot(style='k--')
pyplot.show()


A Grouper allows the user to specify a groupby instruction for an object.
The squeeze() method converts a single column DataFrame into a Series.


from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot
series = read_csv('/content/daily-min-temperatures.csv', header=0, index_col=0, parse_dates=True)
#print(series.head())

series=series.squeeze()
#print(series.head())
groups = series.groupby(Grouper(freq='A'))
#print(groups)
years = DataFrame()
#print(years)
for name, group in groups:
  years[name.year] = group.values
  print(years)
years.plot(subplots=True, legend=False)
pyplot.show()


Histogram and Density Plots

series.hist()
pyplot.show()


Generate Kernel Density Estimate plot using Gaussian kernels.

series.plot(kind='kde')
pyplot.show()


years.boxplot()
pyplot.show()


Box and Whisker Plots by Interval

from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot
series = read_csv('daily-min-temperatures.csv', header=0, index_col=0, parse_dates=True)
series=series.squeeze()
groups = series.groupby(Grouper(freq='A'))
years = DataFrame()
for name, group in groups:
 years[name.year] = group.values
years.boxplot()
pyplot.show()


Heat Maps
from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot
series = read_csv('daily-min-temperatures.csv', header=0, index_col=0, parse_dates=True)
series=series.squeeze()
groups = series.groupby(Grouper(freq='A'))
years = DataFrame()
for name, group in groups:
 years[name.year] = group.values
years = years.T
print(years)
pyplot.matshow(years, interpolation=None, aspect='auto')
pyplot.show()


Lag Scatter Plots

from pandas.plotting import lag_plot
lag_plot(series)
pyplot.show()


Autocorrelation Plots 

from pandas.plotting import autocorrelation_plot
autocorrelation_plot(series)
pyplot.show()



