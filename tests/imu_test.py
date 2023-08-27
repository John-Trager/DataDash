import json
import os
import time
import board
import busio
import numpy as np
import adafruit_mpu6050
import time

imu_offsets_file = "logs/imu_offsets.json"

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

if not os.path.exists(imu_offsets_file):
    print("No imu offset generate please run the calibrate_imu.py script")
    exit(1)


imu_offsets_dict = {}
# get offsets
with open(imu_offsets_file,"r") as json_file:
    imu_offsets_dict = json.load(json_file)

while True:
    t = time.time()
    accel = np.asarray(mpu.acceleration)
    gyro = np.asarray(mpu.gyro)

    accel -= imu_offsets_dict["accel_bias"]
    gyro -= imu_offsets_dict["gyro_bias"]

    """
    print(f"Acceleration: X:{accel[0]:.2f}, Y: {accel[1]:.2f}, Z: {accel[2]:.2f} m/s^2")
    print(f"Gyro X:{gyro[0]:.2f}, Y: {gyro[1]:.2f}, Z: {gyro[2]:.2f} degrees/s")
    print(f"Temperature: {mpu.temperature:.2f} C")
    print("")
    time.sleep(1)
    """

    print(f"{accel[0]}, {accel[1]}, {accel[2]}, {gyro[0]}, {gyro[1]}, {gyro[2]}, {mpu.temperature:.2f}, {t}")
    time.sleep(0.01)