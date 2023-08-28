import board
import busio
import numpy as np
import adafruit_mpu6050
import os
import json
from lib.utils import RollingVarianceCalculator
import threading
import time

imu_offsets_file = "logs/imu_offsets.json"


class MotionDetector:
    def __init__(self, idle_time: int, sample_freq: int, threshold: float) -> None:
        """
        Args:
            idle_time(int): the amount of time in minutes that the device is idle before considered not in motion
            sample_freq(float): frequency (HZ) to read from the IMU
        """
        self.threshold = threshold
        self.sample_freq = sample_freq
        self.end_flag = threading.Event()

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

    def start(self, motion_event: threading.Event):
        # run a thread that reads in from the IMU at sample_freq and adds it to `self.series_var`
        print("starting imu (motionDetection)")
        imu_motion_thread = threading.Thread(
            target=self.read_imu_and_check_motion,
            args=(motion_event),
        )
        imu_motion_thread.start()

    def stop(self):
        self.end_flag.set()

    def read_imu_and_check_motion(self, motion_event):
        while not self.end_flag.is_set():
            accel = np.asarray(self.mpu.acceleration)
            accel -= self.imu_offsets_dict["accel_bias"]

            self.series_var.update(accel)

            var = self.series_var.get_variance()
            if var != None and var < self.threshold:
                motion_event.set()

            time.sleep(1.0 / self.sample_freq)
