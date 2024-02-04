"""
used to explore different params for the motion detector on recorded test data
"""

import csv
import matplotlib.pyplot as plt
from lib.utils import SMAVariance

data_path = "feb3_100hz_imu.csv"

data = {}
# Read the data from the csv file, put each column into a list
with open(data_path, "r") as file:
    reader = csv.reader(file)
    header = next(reader)
    for col in header:
        data[col] = []
    for row in reader:
        for col, value in zip(header, row):
            data[col].append(float(value))

# make the 100hz data into 10hz data by removing 9 out of every 10 data points
# this is to make the data easier to work with
for key in data:
    data[key] = data[key][::10]

# subtract 9.8 from z accel data
# data["accel_z"] = [x - 9.8 for x in data["accel_z"]]

rvc_avg = SMAVariance(300)

data["var_avg"] = []

# calculate the rolling variance for each axis
for x, y, z in zip(data["accel_x"], data["accel_y"], data["accel_z"]):

    rvc_avg.update(x + y + z)

    data["var_avg"].append(rvc_avg.get_var())


# plot x,y,z accel data
plt.plot(data["time_since_epoch"], data["accel_x"], label="x")
plt.plot(data["time_since_epoch"], data["accel_y"], label="y")
plt.plot(data["time_since_epoch"], data["accel_z"], label="z")

# plot avg var of 3 axis
plt.plot(data["time_since_epoch"], data["var_avg"], label="var_avg")

plt.legend()
plt.show()

"""
take away: 


WITH NEW RVC:
10hz 300 win:
lowest in motion 0.075
idle 0.007-0.005
signal to noise: 0.075/0.007 = 10.7


NOTE: The below is what we are currently using
10hz 300 win and new AVG:
lowest in motion 0.216
idle 0.028-0.021
signal to noise: 0.216/0.028 = 7.7

--- 

WITH OLD RVC:

100hz with 50 window size:
    0.02 lowest avg value while in motion
    while stationary avg var between 0.007-0.01

    - so idle threshold should be below 0.02 but above 0.007-0.01
    - motion threshold should be above 0.02 but maybe a good amount higher? 

    signal to noise: 0.02/0.01 = 2


100hz with 500 window size:
    while stationary avg var between 0.007-0.01
    while in motion avg var lowest was 0.039

    signal to noise: 0.039/0.01 = 3.9

    in generally the variance was smoother since this is kinda like a moving average
    this could definitely be better for avoiding false positives but we would want to find a way to make 
    the algorithm more efficient then since the window is so large

10hz with 50 window size:
    while in motion avg var lowest was 0.03
    while stationary avg var between 0.006-0.01

    var avg also seemed to be pretty smooth similar to 100hz with 500 window size
    but not as smooth

10hz with 500 window size:
while in motion avg lowest was 0.09
while stationary avg var between 0.007-0.01

very smooth graph but certainly with a large delay

TODO:
- need to test shorter HZ to see if the variance is the same
- also see how longer var windows change things (should theoretically just smooth it out more?)
"""
