import board
import busio
import numpy as np
import adafruit_mpu6050
import os
import json
from lib.utils import RollingVarianceCalculator, Timer
import threading
import time

imu_offsets_file = "logs/imu_offsets.json"


class MotionDetector:
    def __init__(self, idle_time: int, sample_freq: int, threshold: float, motion_event: threading.Event) -> None:
        """
        Used to detect when there is "no motion" so we know that the device is idle

        Args:
            idle_time(int): the amount of time in seconds that the device is idle before considered not in motion
            sample_freq(float): frequency (HZ) to read from the IMU
            threshold(float): variance threshold of the IMU to consider "no motion"
            motion_event(threading.Event): event to trigger "set" when "no motion" is detected
        """
        self.threshold = threshold
        self.sample_freq = sample_freq
        self.end_flag = threading.Event()
        self.motion_event = motion_event

        i2c = busio.I2C(board.SCL, board.SDA)
        self.mpu = adafruit_mpu6050.MPU6050(i2c)

        if not os.path.exists(imu_offsets_file):
            print("No imu offsets, please run the calibrate_imu.py script")
            exit(1)

        # get offsets
        self.imu_offsets_dict = {}
        with open(imu_offsets_file, "r") as json_file:
            self.imu_offsets_dict = json.load(json_file)

        self.series_var = RollingVarianceCalculator(sample_freq * idle_time)

    def __del__(self):
        self.stop()

    def start(self):
        print("starting imu (motionDetection)")
        imu_motion_thread = threading.Thread(
            target=self.read_imu_and_check_motion,
            args=(),
        )
        imu_motion_thread.start()

    def stop(self):
        self.end_flag.set()

    def read_imu_and_check_motion(self):
        while not self.end_flag.is_set():
            loop_timer = Timer()

            accel = np.asarray(self.mpu.acceleration)
            accel -= self.imu_offsets_dict["accel_bias"]

            # using the X axis value of the accelerometer
            self.series_var.update(accel[0])

            var = self.series_var.variance
            if var != None and var < self.threshold:
                self.motion_event.set()

            sleep_time = max(0,(1.0 / self.sample_freq)-loop_timer.elapsed())
            #print(f"Var: {var}, accel: {accel}, sleep_time: {sleep_time}")
            time.sleep(sleep_time)
