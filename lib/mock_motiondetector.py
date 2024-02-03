from lib.state import State
from lib.utils import log, log_error
import threading
import time
from queue import Queue

class MotionDetectorDummy:
    def __init__(self, queue: Queue) -> None:
        self.queue = queue
        self.state = State.IDLE

        self.enabled_event = threading.Event()
        self.stop_event = threading.Event()
        self.state_lock = threading.Lock()

        # start running thread upon creation
        self.run_t = threading.Thread(target=self.run)
        self.run_t.start()

    def __del__(self) -> None:
        # this order matters
        self.stop_event.set()
        self.enabled_event.set()
        self.run_t.join()

    def start(self):
        self.enabled_event.set()

    def stop(self):
        self.enabled_event.clear()

    def run(self):
        while not self.stop_event.is_set():

            # wait until enabled
            self.enabled_event.wait()

            # have to check again since could have been set
            # while waiting for enable event
            if self.stop_event.is_set():
                break

            with self.state_lock:
                match self.state:
                    case State.IDLE:
                        # print thread id
                        log(
                            f"dummy sent motion detected; {threading.current_thread().ident}"
                        )
                        self.queue.put(("MotionDetection", "motion_detected"))
                        self.state = State.IN_MOTION
                    case State.IN_MOTION:
                        log(
                            f"dummy sent idle detected; {threading.current_thread().ident}"
                        )
                        self.queue.put(("MotionDetection", "idle_detected"))
                        self.state = State.IDLE
                    case _:
                        log_error(f"Invalid state: {self.state}")
                        break

            time.sleep(10)