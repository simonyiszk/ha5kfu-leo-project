import numpy as np
from matplotlib import pyplot as plt

data = np.genfromtxt("data.csv", delimiter=",")

az = data[:, 0]
read = data[:, 2]

read_db = 10*np.log10(read)

#plt.scatter(az, read_db)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot((az+20) / 180 * np.pi, read_db)
ax.set_rticks([-32,-35,-40,-45])
ax.set_xticks(np.array([0, 45, 90-16, 90, 90+16, 135, 180, 180+45, 270, 270+45])*np.pi/180)
ax.set_title("Logarithmic directivity plot")
ax.grid(True)
plt.show()
