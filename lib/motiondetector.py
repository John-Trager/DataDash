from lib.utils import RollingVarianceCalculator, Timer, log_debug
from lib.params import IMU_OFFSET_FILE
from lib.state import State
import adafruit_mpu6050
import board
import busio
import numpy as np
import os
import json
from queue import Queue
import threading
import time

class MotionDetector:
    def __init__(self, idle_time: int, sample_freq: int, thresh_low: float, thresh_high: float,  queue: Queue ) -> None:
        """
        Used to detect if we are in motion or not in motion

        Args:
            idle_time(int): the amount of time in seconds that the device is idle before considered not in motion
            sample_freq(float): frequency (HZ) to read from the IMU
            thresh_low(float): variance threshold of the IMU to consider "no motion"
            thresh_high(float): variance threshold of the IMU to consider "in motion"
            queue(Queue): IPC messsage queue to send when motion state transitions occurs

        !Important call `release()` once done using the motion detector to shut it down properly
        """
        self.sample_freq = sample_freq
        self.thresh_low = thresh_low
        self.thresh_high = thresh_high
        self.queue = queue

        self.rvc = RollingVarianceCalculator(sample_freq * idle_time)

        self.state = State.IDLE
        self.enabled_event = threading.Event()
        self.stop_event = threading.Event()

        i2c = busio.I2C(board.SCL, board.SDA)
        self.mpu = adafruit_mpu6050.MPU6050(i2c)

        if not os.path.exists(IMU_OFFSET_FILE):
            raise RuntimeError(f"No imu offsets at {IMU_OFFSET_FILE}, " \
                                "please run the calibrate_imu.py script")

        # get offsets
        self.imu_offsets_dict = {}
        with open(IMU_OFFSET_FILE, "r") as json_file:
            self.imu_offsets_dict = json.load(json_file)


        # start running thread upon creation 
        # do last, once everything else is intialized
        self.run_t = threading.Thread(target=self.read_imu_and_check_motion)
        self.run_t.start()
    
    def start(self):
        '''
        Start monitoring for motion and motion state transitions.
        Resets state, msg queue, and RVC buffer to remove stale data and state
        '''
        assert self.run_t is not None

        self.reset()
        self.enabled_event.set()

    def stop(self):
        '''
        temporarily stop the motion detector from 
        reading the sensor values and updating its state
        '''
        assert self.run_t is not None
        
        self.enabled_event.clear()

    def reset(self):
        '''
        clears all messages in message queue,
        sets state to IDLE,
        clears RVC buffer
        '''
        assert not self.enabled_event.is_set()

        # clear all messages in queue
        while not self.queue.empty():
            self.queue.get()

        self.state = State.IDLE
        self.rvc.reset()

    def release(self):
        '''
        Releases motiondector device.
        Once this is called the motion detection instance 
        can no longer be used.
        '''
        # order matters
        self.stop_event.set()
        self.enabled_event.set()
        if self.run_t != None:
            self.run_t.join()
            self.run_t = None

    def read_imu_and_check_motion(self):
        while not self.stop_event.is_set():
            
            # wait until enabled
            self.enabled_event.wait()
            
            loop_timer = Timer()

            # have to check again since could have been set
            # while waiting for enable event
            if self.stop_event.is_set():
                break

            accel = np.asarray(self.mpu.acceleration)
            accel -= self.imu_offsets_dict["accel_bias"]

            # using the X axis value of the accelerometer
            self.rvc.update(accel[0])

            var = self.rvc.variance

            match self.state:
                case State.IDLE:
                    if var != None and var > self.thresh_high:
                        self.state = State.IN_MOTION
                        self.queue.put(("MotionDetector", "motion_detected"))
                case State.IN_MOTION:
                    if var != None and var < self.thresh_low:
                        self.state = State.IDLE
                        self.queue.put(("MotionDetector", "idle_detected"))   

            sleep_time = max(0,(1.0 / self.sample_freq)-loop_timer.elapsed())
            log_debug(f"Var: {var}, accel: {accel}, sleep_time: {sleep_time}, state: {self.state}")
            time.sleep(sleep_time)