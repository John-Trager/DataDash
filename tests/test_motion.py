from lib.motiondetector import MotionDetector
import threading

if __name__ == "__main__":

    still_motion_event = threading.Event()
    motionDetector = MotionDetector(30, 5, 0.1, still_motion_event)
 
    motionDetector.start()

    # wait until no "motion" is detected
    still_motion_event.wait()

    motionDetector.stop()