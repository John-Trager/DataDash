from utils import log, get_string_time_now
from params import IMU_OFFSET_FILE
import adafruit_mpu6050
import board
import busio
import json
import time
from tqdm import tqdm

GRAVITY_CONST = 9.80665

if __name__ == '__main__':
    i2c = busio.I2C(board.SCL, board.SDA)
    mpu = adafruit_mpu6050.MPU6050(i2c)

    gyro_bias = [0, 0, 0]
    accel_bias = [0, 0, 0]
    num_readings = 1000 

    log("Calculating IMU bias offsets")
    for _ in tqdm(range(num_readings)):
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

    log("Finished bias calculation!")
    log(f"accel bias: {accel_bias}")
    log(f"gyro bias: {gyro_bias}")

    params = {"sample_time": get_string_time_now(),
              "accel_bias": accel_bias, 
              "gyro_bias": gyro_bias}

    with open(IMU_OFFSET_FILE, "w") as json_file:
        json.dump(params, json_file, indent=4)

    log("Saved bias offsets to json!")

