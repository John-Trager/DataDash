from lib.motiondetector import MotionDetector
from lib.utils import log
from queue import Queue

if __name__ == '__main__':
    log("starting")

    q = Queue()
    md = MotionDetector(10, 5, 0.1, 0.5, q)

    md.start()
    # wait until no "motion" is detected
    num_trans = 0

    while num_trans < 3:
        sender, message = q.get()
        log(f"recv message: {sender}, {message}")
        num_trans += 1
    
    md.release()
    log("done")