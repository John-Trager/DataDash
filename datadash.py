"""

"""
from lib.lcd16x2 import LCD
from lib.motiondetector import MotionDetector
from lib.state import State
from lib.utils import *
from lib.datarecorder import DataRecorder
from lib.uploader import Uploader
from queue import Empty, Queue
from loguru import logger

class DataDash:

    def __init__(
        self,
        data_dir: str = "data",
        remote_dir: str = "data",
        idle_timeout: int = 60,
        server_timeout: int = 30,
    ) -> None:
        """
        DataDash object and state machine

        Args:
            data_dir(str): path to dir where data will be stored before being uploaded
            remote_dir(str): path to dir on remote server where data will be stored
            idle_timeout(int): idle timeout in seconds, if timeout occurs will shutdown
            server_timeout(int): server timeout in seconds,
                how long will try to connect to server before giving up
        """
        self.idle_timeout = idle_timeout
        self.server_timeout = server_timeout
        self.state = State.IDLE  # initial state
        self.queue = Queue()  # queue only used by md

        self.recorder = DataRecorder(data_dir, "tmp", 0, 30, 1280, 960)
        self.uploader = Uploader(data_dir, remote_dir)

        self.lcd = LCD()

        # intialize last
        self.motion_detector = MotionDetector(30, 10, 0.05, 0.3, self.queue)
        logger.debug("*** DataDash intialized ***")

    def idle(self) -> State:
        logger.info("idle")
        self.lcd.display(f"{self.state}")

        # start the motion detector
        self.motion_detector.start()

        # now wait until we receive message
        # from detector or timeout
        try:
            sender, message = self.queue.get(timeout=self.idle_timeout)
            logger.info(f"recv message: {sender}, {message}")
        except Empty:
            logger.info("timeout occurred")
            self.state = State.DONE
            return self.state

        if message == "motion_detected":
            self.state = State.IN_MOTION
        else:
            logger.error(f"Invalid message: {message}")
            self.state = State.DONE

        return self.state

    def in_motion(self) -> State:
        logger.info("in motion")
        self.lcd.display(f"{self.state}")

        self.recorder.start()

        # wait for idle message from detector
        # TODO: consider adding timeout
        # TODO: consider adding md heartbeat or fail-safe
        # because if the sensor fails we will record forever
        try:
            sender, message = self.queue.get()
            logger.info(f"recv message: {sender}, {message}")
        except Empty:
            logger.info("timeout occurred")
            self.recorder.stop()
            self.state = State.DONE
            return

        if message == "idle_detected":
            self.state = State.WAIT_FOR_UPLOAD
        else:
            logger.error(f"Invalid message: {message}")
            self.state = State.DONE

        # on in_motion exit
        self.recorder.stop()
        self.motion_detector.stop()

        return self.state

    def wait_for_upload(self) -> State:
        logger.info("wait for upload")
        self.lcd.display(f"{self.state}")

        start = Timer()

        # try to re-connect 1/sec until timeout
        while start.elapsed() < self.server_timeout:
            reachable = server_reachable()

            if reachable:
                self.state = State.UPLOAD_STATE
                return self.state

            time.sleep(1)

        self.state = State.IDLE
        logger.warning("failed to connect to server, going to IDLE")

        return self.state

    def upload(self) -> State:
        logger.info("upload state")
        self.lcd.display(f"{self.state}")

        result = None

        try:
            result = self.uploader.upload()
        except Exception as e:
            logger.error(e)
            self.state = State.DONE
            return self.state

        if result:
            self.state = State.IDLE
        else:
            self.state = State.WAIT_FOR_UPLOAD

        return self.state

    def done(self) -> None:
        logger.info("done")
        self.motion_detector.release()
        self.recorder.release()
        # maybe do something different here
        # so we can see that we are done
        self.lcd.release() 
        logger.info("released devices")


if __name__ == "__main__":
    setup_logger()
    dd = DataDash()

    # note that some of the function calls are
    # blocking or will take a while so this won't loop fast always
    while True:
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
                logger.error(f"Invalid state: {dd.state}")
                break

    logger.info("main program end")
