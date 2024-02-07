from lib.oakdcam import depthCam
import time

if __name__ == "__main__":
    cam = depthCam()
    cam.start_recording("test_depth_cam", "tmp", "data")
    time.sleep(5)
    cam.stop_recording()
    cam.release()
