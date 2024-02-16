from lib.motiondetector import MotionDetector
from queue import Queue
from loguru import logger

if __name__ == '__main__':
    logger.info("starting")

    q = Queue()
    md = MotionDetector(10, 5, 0.1, 0.5, q)

    md.start()
    # wait until no "motion" is detected
    num_trans = 0

    while num_trans < 3:
        sender, message = q.get()
        logger.info(f"recv message: {sender}, {message}")
        num_trans += 1
    
    md.release()
    logger.info("done")