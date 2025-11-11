Aim: Implementing auto correlation and partial auto-correlation on timeseries


# ACF plot of time series
from pandas import read_csv
from matplotlib import pyplot
#from statsmodels.graphics.tsaplots import plot_acf
from pandas.plotting import autocorrelation_plot
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-min-temperatures.csv', header=0, index_col=0,parse_dates=True, squeeze=True)
#plot_acf(series)
autocorrelation_plot(series)
pyplot.show()




*********


# zoomed-in ACF plot of time series
from pandas import read_csv
from matplotlib import pyplot
from statsmodels.graphics.tsaplots import plot_acf
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-min-temperatures.csv', header=0, index_col=0,parse_dates=True, squeeze=True)
plot_acf(series, lags=50)
pyplot.show()



**************



# PACF plot of time series
from pandas import read_csv
from matplotlib import pyplot
from statsmodels.graphics.tsaplots import plot_pacf
series = read_csv('/content/drive/MyDrive/MScDS TSA/daily-min-temperatures.csv', header=0, index_col=0,
parse_dates=True, squeeze=True)
plot_pacf(series, lags=50)
pyplot.show()



***************8







