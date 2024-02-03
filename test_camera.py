from lib.camera import Camera
import time

if __name__ == '__main__':

    cam = Camera(0, 32, 1280, 960)

    time.sleep(5)

    print("working...")

    cam.release()