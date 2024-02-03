"""
This is the data recorder service

Currently handles recording video data from a connected camera
"""
from lib.utils import log_debug
from lib.camera import Camera
from datetime import datetime
from pathlib import Path


class DataRecorder:
    def __init__(
        self,
        data_path: str,
        tmp_path: str,
        video_p: int,
        framerate: int,
        width: int,
        height: int,
    ) -> None:
        """
        Args:
            data_path(str): where to put videos that are finished recording and ready for upload
            tmp_path(str): where to store videos that are in progress of recording
            video_p(int): port camera is on (usually 0)
            framerate(int): camera framerate
            width(int): width resolution of the camera
            height(int): height resolution of the camera
        """
        self.cam = Camera(video_p, framerate, width, height)
        self.tmp_path = tmp_path
        self.data_path = data_path

        # create directories if they don't exist yet
        Path(tmp_path).mkdir(parents=True, exist_ok=True)
        Path(data_path).mkdir(parents=True, exist_ok=True)

        log_debug("DataRecorder intialized")


    def start(self):
        '''Starts recording data'''
        # TODO: consider having a check that makes sure there is enough space on the device

        # name format: MM-DD-YYYY_HH:MM:SS
        record_filename = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
        self.cam.start_recording(record_filename, self.tmp_path, self.data_path)

    def stop(self):
        '''Stops recording data'''
        # update
        self.cam.stop_recording()

    def release(self):
        self.cam.release()
