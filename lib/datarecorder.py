"""
This is the data recorder service
"""
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
        self.cam = Camera(video_p, framerate, width, height)
        self.tmp_path = tmp_path
        self.data_path = data_path

        # create directories if they don't exist yet
        Path(tmp_path).mkdir(parents=True, exist_ok=True)
        Path(data_path).mkdir(parents=True, exist_ok=True)

    def start(self):
        # TODO: consider having a check that makes sure there is enough space on the device

        # name format: MM-DD-YYYY_HH:MM:SS
        record_filename = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
        self.cam.start_recording(record_filename, self.tmp_path, self.data_path)

    def stop(self):
        # update
        self.cam.stop_recording()
