from depthai_sdk import OakCamera, RecordType
from multiprocessing import Process, Event
import shutil
from utils import log_warn


class OakdCam:
    def __init__(self):
        self.end_event = Event()

    def start_recording(self, filename: str, temp_path: str, data_path: str):
        self.record_process = Process(
            target=self.record, args=(filename, temp_path, data_path)
        )
        self.record_process.start()

    def stop_recording(self):
        self.end_event.set()
        if self.record_process is not None:
            self.record_process.join()

    def release(self):
        pass

    def record(self, filename: str, temp_path: str, data_path: str):

        filename += ".mp4"
        out_path = None

        with OakCamera() as oak:
            color = oak.create_camera(
                "color", resolution="1080P", fps=50, encode="H265"
            )
            handler = oak.record(color.out.encoded, temp_path, RecordType.VIDEO)
            oak.visualize(color.out.camera, scale=2 / 3, fps=True)
            oak.start(blocking=False)
            while not self.end_event.is_set() and oak.running():
                oak.poll()

            out_path = handler.recorder.path

        if out_path is None:
            log_warn(
                "No output file path detected from oakd, Recording may have failed"
            )
            return

        # Move the file to the data path
        # move out_path/CAM_A_bitstream.mp4 to data_path/filename
        shutil.move(f"{out_path}/CAM_A_bitstream.mp4", f"{data_path}/{filename}")

        # delete the out_path folder and contents
        shutil.rmtree(out_path)
