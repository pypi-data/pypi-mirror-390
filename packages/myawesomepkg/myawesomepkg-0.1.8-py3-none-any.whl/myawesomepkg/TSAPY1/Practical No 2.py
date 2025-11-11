Practical No 2 Aim: Implementing timeseries components
Seasonality
Trend
Pattern
Cyclic


Draw random samples from a normal (Gaussian) distribution.
upword downword horizontal and non-lenear trend

import numpy as np
import matplotlib.pyplot as plt

# Upward Trend
t = np.arange(0, 10, 0.1)
data = t + np.random.normal(0, 0.5, len(t))
plt.plot(t, data, label='Upward Trend')

# Downward Trend
t = np.arange(0, 10, 0.1)
data = -t + np.random.normal(0, 0.5, len(t))
plt.plot(t, data, label='Downward Trend')

# Horizontal Trend
t = np.arange(0, 10, 0.1)
data = np.zeros(len(t)) + np.random.normal(0, 0.5, len(t))
plt.plot(t, data, label='Horizontal Trend')

# Non-linear Trend
t = np.arange(0, 10, 0.1)
data = t**2 + np.random.normal(0, 0.5, len(t))
plt.plot(t, data, label='Non-linear Trend')

plt.legend()
plt.show()



weekly monthly yearly seasonality

import numpy as np
import matplotlib.pyplot as plt

# generate sample data with different types of seasonality
np.random.seed(1)
time = np.arange(0, 366)

# weekly seasonality
weekly_seasonality = np.sin(2 * np.pi * time / 7)
weekly_data = 5 + weekly_seasonality

# monthly seasonality
monthly_seasonality = np.sin(2 * np.pi * time / 30)
monthly_data = 5  + monthly_seasonality

# annual seasonality
annual_seasonality = np.sin(2 * np.pi * time / 365)
annual_data = 5 + annual_seasonality

# plot the data
plt.figure(figsize=(12, 8))
plt.plot(time, weekly_data,label='Weekly Seasonality')
plt.plot(time, monthly_data,label='Monthly Seasonality')
plt.plot(time, annual_data,label='Annual Seasonality')
plt.legend(loc='upper left')
plt.show()



cyclic time series data

import numpy as np
import matplotlib.pyplot as plt

# Generate sample data with cyclic patterns
np.random.seed(1)
time = np.array([0, 30, 60, 90, 120,
                 150, 180, 210, 240,
                 270, 300, 330])
data = 10 * np.sin(2 * np.pi * time / 50) + 20 * np.sin(2 * np.pi * time / 100)

# Plot the data
plt.figure(figsize=(12, 8))
plt.plot(time, data, label='Cyclic Data')
plt.legend(loc='upper left')
plt.xlabel('Time (days)')
plt.ylabel('Value')
plt.title('Cyclic Time Series Data')
plt.show()



original data  and data with irregularity

import numpy as np
import matplotlib.pyplot as plt

# Generate sample time series data
np.random.seed(1)
time = np.arange(0, 100)
#data = 5 * np.sin(2 * np.pi * time / 20) + 2 * time
data=np.sin(2 * np.pi * time / 30)+time

# Introduce irregularities by adding random noise
irregularities = np.random.normal(0, 5, len(data))
irregular_data = data + irregularities

# Plot the original data and the data with irregularities
plt.figure(figsize=(12, 8))
plt.plot(time, data, label='Original Data')
plt.plot(time, irregular_data,label='Data with Irregularities')
plt.legend(loc='upper left')
plt.show()


