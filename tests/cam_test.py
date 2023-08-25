import numpy as np
import cv2 as cv

video_file_name = "output"

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FPS, 30)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)   
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 960)

off_by_factor = 0.8

# Verify if settings are set
frame_rate = cap.get(cv.CAP_PROP_FPS)
frame_width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)

print(f"Frame rate: {frame_rate}")
print(f"Frame width: {frame_width}")
print(f"Frame height: {frame_height}")

fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter(f"{video_file_name}.mp4", fourcc, off_by_factor*30.0,(1280,960))


if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # write the frame
    out.write(frame)
    # Display the resulting frame
    cv.imshow('frame', frame)

    if cv.waitKey(1) == ord('q'):
        break
    # When everything done, release the capture

cap.release()
out.release()
cv.destroyAllWindows()

