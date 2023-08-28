from lib.datarecorder import DataRecorder
from lib.datauploader import DataUploader
from lib.motiondetector import MotionDetector
import time
import threading

if __name__ == "__main__":
    recorder = DataRecorder("data", "data_tmp", 0, 30, 1280, 960)
    uploader = DataUploader("http://localhost:8001/upload", "data", "logs", 5, 10, True)
    motionDetector = MotionDetector(5, 5, 0.1)

    ## Start the different processes
    uploader.start()
    recorder.start()
    still_motion_event = threading.Event()
    motionDetector.start(still_motion_event)

    # wait until no "motion" is detected
    still_motion_event.wait()

    motionDetector.stop()
    recorder.stop()
    uploader.stop()
