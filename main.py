from lib.datarecorder import DataRecorder
from lib.datauploader import DataUploader
from lib.motiondetector import MotionDetector
import time
import threading

if __name__ == "__main__":

    recorder = DataRecorder("data", "data_tmp", 0, 60, 1920, 1080)
    uploader = DataUploader(
        "http://server1.local:8001/upload", "data", "logs", 5, 10, False
    )

    # wait until no "motion" is detected
    still_motion_event = threading.Event()
    motionDetector = MotionDetector(60*5, 5, 0.1, still_motion_event)

    ## Start the different processes
    uploader.start()
    recorder.start()
    motionDetector.start()

    # wait until no "motion" is detected
    still_motion_event.wait()

    motionDetector.stop()
    recorder.stop()
    print("waiting for uploader to stop...")
    time.sleep(12)
    uploader.stop()

    # TODO: maybe join on the other threads before this?
    # or just note that they may still be running for a little bit
    print("main program has finished (other threads may be finishing up)")

