from lib.datarecorder import DataRecorder
from lib.datauploader import DataUploader
from lib.motiondetector import MotionDetector
import time

# time between checking pos for motion
MOTION_TIMEOUT = 60 * 4

if __name__ == "__main__":
    recorder = DataRecorder("data", "data_tmp", 0, 30, 1280, 960)
    uploader = DataUploader("http://localhost:8001/upload", "data", "logs", 5, 10, True)
    motionDetector = MotionDetector(5)

    ## Start the different processes
    uploader.start()
    recorder.start()

    # start the motion detection
    motionDetector.initialize()

    while motionDetector.in_motion():
        time.sleep(MOTION_TIMEOUT)

    recorder.stop()
    uploader.stop()
