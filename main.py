from lib.datarecorder import DataRecorder
from lib.datauploader import DataUploader
import time

if __name__ == "__main__":
    # recorder = DataRecorder("data", "data_tmp", 0, 30, 1280, 960)
    uploader = DataUploader("http://localhost:8001/upload", "data", "logs", 5, 10, True)

    # recorder.start()

    uploader.start()

    time.sleep(5)

    # recorder.stop()
    uploader.stop()
