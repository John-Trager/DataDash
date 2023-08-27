import numpy as np
from filterpy.kalman import KalmanFilter
import json
import os
import time
import board
import busio
import adafruit_mpu6050


# Create a Kalman filter
kf = KalmanFilter(dim_x=2, dim_z=1)  # 2D state (velocity, acceleration), 1D measurement (acceleration)
dt = 0.01 # Time step
kf.x = np.array([0.0, 0.0]).T          # Initial state (velocity, acceleration)
kf.P *= 0.01                          # Initial uncertainty
kf.R = 0.001                           # Measurement noise (variance)
kf.Q = np.array([[1., 1.],       # Process noise covariance matrix
                 [1., 1.]])

kf.F = np.array([[1.0, dt],    # State transition matrix
                 [0.0, 1.0]])

kf.H = np.array([[0.0, 1.0]])   # Observation matrix



### IMU stuff
# Assuming that we are getting accel_x from the accelerometer and integrating it to get the velocity
imu_offsets_file = "logs/imu_offsets.json"

if not os.path.exists(imu_offsets_file):
    print("No imu offset generate please run the calibrate_imu.py script")
    exit(1)

imu_offsets_dict = {}
# get offsets
with open(imu_offsets_file,"r") as json_file:
    imu_offsets_dict = json.load(json_file)

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

###

while True:

    accel = np.asarray(mpu.acceleration) - imu_offsets_dict["accel_bias"]
    
    kf.predict()
    kf.update(np.array([accel[1]]))
    print(kf.x[0], accel[1])
