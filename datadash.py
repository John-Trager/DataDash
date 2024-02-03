"""

"""

from lib.state import State
from lib.utils import *
from lib.datarecorder import DataRecorder
from lib.uploader import Uploader
import threading
from queue import Empty, Queue
import time


class MotionDetectionDummy:
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


class DataDash:

    def __init__(
        self,
        data_dir: str = "data",
        remote_dir: str = "data",
        idle_timeout: int = 30,
        server_timeout: int = 30,
    ) -> None:
        self.idle_timeout = idle_timeout
        self.state = State.IDLE  # initial state
        self.queue = Queue()

        self.motion_detector = MotionDetectionDummy(self.queue)
        self.recorder = DataRecorder(data_dir, "tmp", 0, 30, 1280, 960)
        self.uploader = Uploader(data_dir, remote_dir)

    def idle(self) -> State:
        log("idle")

        # start the motion detector
        self.motion_detector.start()

        # now wait until we receive message
        # from detector or timeout
        try:
            sender, message = self.queue.get(timeout=self.idle_timeout)
            log(f"recv message: {sender}, {message}")
        except Empty:
            log("timeout occurred")
            self.state = State.DONE
            return self.state

        if message == "motion_detected":
            self.state = State.IN_MOTION
        else:
            log_error(f"Invalid message: {message}")
            self.state = State.DONE

        return self.state

    def in_motion(self) -> State:
        log("in motion")

        self.recorder.start()

        # wait for idle message from detector
        # TODO: consider adding timeout
        try:
            sender, message = self.queue.get()
            log(f"recv message: {sender}, {message}")
        except Empty:
            log("timeout occurred")
            self.recorder.stop()
            self.state = State.DONE
            return

        if message == "idle_detected":
            self.state = State.WAIT_FOR_UPLOAD
        else:
            log_error(f"Invalid message: {message}")
            self.state = State.DONE

        self.recorder.stop()

        return self.state

    def wait_for_upload(self) -> State:
        log("wait for upload")

        reachable = server_reachable()

        if reachable:
            self.state = State.UPLOAD_STATE
        else:
            # TODO: consider adding a retry if we don't
            # ping successfully the first time
            self.state = State.DONE

        return self.state

    def upload(self) -> State:
        log("upload state")

        all_uploaded = self.uploader.upload()

        if not all_uploaded:
            self.state = State.WAIT_FOR_UPLOAD
        else:
            self.state = State.IDLE

    def done(self) -> None:
        log("done")
        self.motion_detector.stop()
        # just in case
        self.recorder.stop()


if __name__ == "__main__":
    dd = DataDash()

    # note that some of the function calls are
    # blocking or will take a while so this won't loop fast always
    while dd.state != State.DONE:
        match dd.state:
            case State.IDLE:
                dd.idle()
            case State.IN_MOTION:
                dd.in_motion()
            case State.WAIT_FOR_UPLOAD:
                dd.wait_for_upload()
            case State.UPLOAD_STATE:
                dd.upload()
            case State.DONE:
                dd.done()
                break
            case _:
                log_error(f"Invalid state: {dd.state}")
                break
