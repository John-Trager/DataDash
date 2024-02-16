from lib.oakdcam import OakdCam
import time

if __name__ == "__main__":
    cam = OakdCam()
    cam.start_recording("test_depth_cam", "tmp", "data")
    time.sleep(20)
    cam.stop_recording()
    cam.release()
