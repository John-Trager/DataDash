'''
use this script to test out different confiugrations and see errors more clearly 
then when running the camera in a seperate procress
'''
from multiprocessing import Process, Event
import time

stop_event = Event()

def record():
    # crashes unless I put the import here
    # TODO: fix this as this likely is a performance issue
    from depthai_sdk import OakCamera, RecordType

    with OakCamera() as oak:
            color = oak.create_camera(
                "color", resolution="1080P", fps=50, encode="H265"
            )
            handler = oak.record(color.out.encoded, "tmp/", RecordType.VIDEO)
            oak.start(blocking=False)
            while not stop_event.is_set() and oak.running():
                oak.poll()


if __name__ == '__main__':
    
    record_process = Process(target=record)
    record_process.start()
    time.sleep(5)
    stop_event.set()
    record_process.join()