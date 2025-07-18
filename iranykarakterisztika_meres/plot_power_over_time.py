import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import datetime as dt

data = np.loadtxt("data.csv", delimiter=",", dtype=float)
dates=[dt.datetime.fromtimestamp(ts) for ts in data[:, 0]]
value = data[:, 1]

plt.plot(dates,value, "--,")
plt.show()
