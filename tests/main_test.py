from lib.camera import Camera
import time


if __name__ == "__main__":
    cam = Camera(0, 30, 1280, 960)

    print("star_recording()")
    cam.start_recording("file")

    time.sleep(5)
    print("stop_recording()")
    cam.stop_recording()

    print("end")
