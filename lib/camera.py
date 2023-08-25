"""
a camera class for a USB connected camera
"""
import cv2 as cv
import threading
import shutil
import os

# TODO: find the correct offset...
OFFSET = 0.85


class Camera:
    def __init__(self, video_p: int, framerate: int, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.fps = framerate

        self.cap = cv.VideoCapture(video_p)

        self.cap.set(cv.CAP_PROP_FPS, framerate)  # 30
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)  # 1280
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)  # 960

        self.end_flag = threading.Event()

    def __del__(self) -> None:
        self.stop_recording()
        self.cap.release()

    def start_recording(self, filename: str, temp_path: str, data_path: str) -> None:
        record_thread = threading.Thread(
            target=self.recording,
            args=(
                filename,
                temp_path,
                data_path,
                self.end_flag,
            ),
        )
        record_thread.start()

    def stop_recording(self) -> None:
        self.end_flag.set()

    def recording(
        self, filename: str, temp_path: str, data_path: str, end_flag: threading.Event
    ) -> None:
        print("start recording")

        # TODO: consider having a max time limit for a recording
        # where once it hits the limit it creates a new file
        # this could aid with uploading data

        filename += ".mp4"

        # initial location for recording while it is in progress
        temp_file_path = os.path.join(temp_path, filename)
        # move file to this path once recording is completed
        data_file_path = os.path.join(data_path, filename)

        print(temp_file_path, data_file_path)

        fourcc = cv.VideoWriter_fourcc(*"mp4v")
        out = cv.VideoWriter(
            temp_file_path,
            fourcc,
            OFFSET * self.fps,
            (self.width, self.height),
        )

        if not self.cap.isOpened():
            print("Error: Cannot open camera!")
            return

        while not end_flag.is_set():
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # write the frame
            out.write(frame)

        print("ending recording")

        out.release()

        # move file from temp location to data location
        shutil.move(temp_file_path, data_file_path)
