"""
a camera class for a USB connected camera
"""

from lib.params import CAM_OFFSET
from lib.utils import *
import cv2 as cv
import threading
from loguru import logger
import shutil
import os


class Camera:
    def __init__(self, video_p: int, framerate: int, width: int, height: int) -> None:
        """
        Args:
            video_p(int): port camera is on (usually 0)
            framerate(int): camera framerate
            width(int): width resolution of the camera
            height(int): height resolution of the camera
        """
        self.width = width
        self.height = height
        self.fps = framerate

        self.cap = cv.VideoCapture(video_p, cv.CAP_V4L2)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)  # 1280
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)  # 960
        self.cap.set(cv.CAP_PROP_FPS, framerate)  # 30

        if not self.cap.isOpened():
            raise RuntimeError("Error: Unable to open Camera. " \
                               f"Is it plugged in and connected on the video port: {video_p}?")

        self.end_flag = threading.Event()
        self.record_thread = None

        logger.debug("Camera intialized")


    def release(self) -> None:
        self.stop_recording()
        self.cap.release()

    def start_recording(self, filename: str, temp_path: str, data_path: str) -> None:
        self.end_flag.clear()
        self.record_thread = threading.Thread(
            target=self.recording,
            args=(
                filename,
                temp_path,
                data_path,
                self.end_flag,
            ),
        )
        self.record_thread.start()

    def stop_recording(self) -> None:
        self.end_flag.set()
        if self.record_thread is not None:
            self.record_thread.join()

    def recording(
        self, filename: str, temp_path: str, data_path: str, end_flag: threading.Event
    ) -> None:
        logger.info("starting recording")

        # TODO: consider having a max time limit for a recording
        # where once it hits the limit it creates a new file
        # this could aid with uploading data

        filename += ".mp4"

        # initial location for recording while it is in progress
        temp_file_path = os.path.join(temp_path, filename)
        # move file to this path once recording is completed
        data_file_path = os.path.join(data_path, filename)

        logger.info(f"temp filepath and name: {temp_file_path}")
        logger.info(f"final filepath and name: {data_file_path} (once recording has finished)")

        fourcc = cv.VideoWriter_fourcc(*"mp4v")
        fps = self.cap.get(cv.CAP_PROP_FPS)
        logger.info(f"FPS set as: {fps}")

        out = cv.VideoWriter(
            temp_file_path,
            fourcc,
            fps,
            (self.width, self.height),
        )

        if not self.cap.isOpened():
            logger.error("Error: Cannot open camera!")
            return

        while not end_flag.is_set():
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            # if frame is read correctly ret is True
            if not ret:
                logger.error("Can't receive frame (stream end?). Exiting ...")
                break

            # write the frame
            out.write(frame)

        logger.info("ending recording")

        out.release()

        # move file from temp location to data location
        shutil.move(temp_file_path, data_file_path)
