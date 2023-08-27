import numpy as np
from filterpy.kalman import KalmanFilter
import json
import os
import time
import board
import busio
import adafruit_mpu6050

kf = KalmanFilter(dim_x=2, dim_z=1)

dt = 0.01 # Time step

# State transition matrix
kf.F = np.array([[1, dt],
                 [0, 1]], dtype=float)

# Measurement function
# [velocity, acceleration]
# we can only measure accleration...
kf.H = np.array([[0, 1]])

# intial state estimation [velocity, acceleration]
kf.x = np.array([[0, 0]]).T

# Covariance matrix
# TODO: unsure how to determine this
kf.P *= 1.

# Measurement noise covariance
# TODO: unsure how to determine this
kf.R = 0.01

# TODO: unsure how to determine this
# Process noise covariance
kf.Q = np.array([[1e-5, 0.],
                 [0., 1e-4]])


### Initialize IMU

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

# Initialize variables
prev_time = time.monotonic()
prev_accel = 0.0

while True:
    current_time = time.monotonic()
    dt = current_time - prev_time
    accel = np.asarray(mpu.acceleration)
    gyro = np.asarray(mpu.gyro)

    accel -= imu_offsets_dict["accel_bias"]
    gyro -= imu_offsets_dict["gyro_bias"]

    # Predict based on the model
    kf.predict()
    
    # Measurement Update
    kf.update([accel[0]]) 

    # Estimated velocity
    print(kf.x[1][0]) 

    time.sleep(dt)