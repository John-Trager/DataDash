import os
import json
import time
import board
import busio
import adafruit_mpu6050

GRAVITY_CONST = 9.80665
log_path = "logs"
param_name = "imu_offsets.json"

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

gyro_bias = [0, 0, 0]
accel_bias = [0, 0, 0]
num_readings = 1000 

print("Calculating biases...")
for _ in range(num_readings):
    accel = mpu.acceleration
    gyro = mpu.gyro

    accel_bias[0] += accel[0]
    accel_bias[1] += accel[1]
    accel_bias[2] += accel[2] - GRAVITY_CONST

    gyro_bias[0] += gyro[0]
    gyro_bias[1] += gyro[1]
    gyro_bias[2] += gyro[2]
    
    time.sleep(0.01)  # Add delay between readings 

# Calculate average biases
accel_bias[0] /= num_readings
accel_bias[1] /= num_readings
accel_bias[2] /= num_readings

gyro_bias[0] /= num_readings
gyro_bias[1] /= num_readings
gyro_bias[2] /= num_readings

print("Finished bias calculation!")

print(f"accel bias: {accel_bias}")
print(f"gyro bias: {gyro_bias}")

print("Finished bias calculation!")

params = {"accel_bias": accel_bias, "gyro_bias": gyro_bias}

with open(os.path.join(log_path, param_name), "w") as json_file:
    json.dump(params, json_file, indent=4)

print("Saved bias offsets to json!")

