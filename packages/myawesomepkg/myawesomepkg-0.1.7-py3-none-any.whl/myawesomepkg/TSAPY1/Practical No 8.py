Aim: Forecasting using ARIMA model --TEMPERATURE 
Time Series Forecasting With ARIMA Model in Python for Temperature Prediction.

1) Reading Time Series Data in Python using Pandas library

import pandas as pd
df=pd.read_csv('/content/drive/MyDrive/MScDS TSA/MaunaLoaDailyTemps.csv',index_col='DATE',parse_dates=True)
df=df.dropna()
print('Shape of data',df.shape)
df.head()
df

**********

df['AvgTemp'].plot(figsize=(12,5))


*******

2) Checking for stationarity of time series model


from statsmodels.tsa.stattools import adfuller
def adf_test(dataset):
     dftest = adfuller(dataset, autolag = 'AIC')
     print("1. ADF : ",dftest[0])
     print("2. P-Value : ", dftest[1])
     print("3. Num Of Lags : ", dftest[2])
     print("4. Num Of Observations Used For ADF Regression:",      dftest[3])
     print("5. Critical Values :")
     for key, val in dftest[4].items():
         print("\t",key, ": ", val)
adf_test(df['AvgTemp'])


*************


 Auto Arima Function to select order of Auto Regression Model

pip install pmdarima



from pmdarima import auto_arima
import warnings
warnings.filterwarnings("ignore")
stepwise_fit=auto_arima(df['AvgTemp'],trace=True,suppress_warnings=True)
stepwise_fit.summary()



************8


Split Your Dataset

print(df.shape)
train=df.iloc[:-30]
test=df.iloc[-30:]
print(train.shape,test.shape)





from statsmodels.tsa.arima.model import ARIMA
model=ARIMA(train['AvgTemp'],order=(1,0,5))
model=model.fit()
model.summary()




**************



Check How Good Your Model Is


start=len(train)
end=len(train)+len(test)-1
pred=model.predict(start=start,end=end,typ='levels').rename('ARIMA Predictions')
print(pred)
pred.index=df.index[start:end+1]
pred.plot(legend=True)
test['AvgTemp'].plot(legend=True)





***********8


Check your Accuracy Metric


from sklearn.metrics import mean_squared_error
from math import sqrt
test['AvgTemp'].mean()
rmse=sqrt(mean_squared_error(pred,test['AvgTemp']))
print(rmse)




