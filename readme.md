# DataDash
The goal of this project is to collect data from a cars dash cam and upload it to the cloud or remote storage once connected to wifi.


## Implementation
The `main.py` file runs the 3 services below all in seperate threads:

- Data Recorder: Records camera data (+ other possible data) and stores on disk (has an additional thread for the Camera)
- Data Uploader: Keeps track of what files have been uploaded and uploads data when a network is available
- Motion Detector: Tracks when the device is in motion and signals when there has been no motion for some period of time
    - Thus we can shut the device down once it has not been in motion for some time

## Hardware
The device is made up of:
- 2 Raspberry PIs (one for the recording device, 1 for the remote video storage)
- logitech USB webcam
- Adafruit MPU/IMU 6050

I have also experimented with a simple GPS module that I had but due to its long-wait time in acquiring satelites it is currently not in use. I have also thought about using a "elm327 obdii bluetooth adapter" to read data directly from the vehicle we are in (such as speed, rpm, etc) but this will have to be done at a later date.

## What's Next
- [x] Working device
- [ ] Further testing the device in the field
- [ ] Web interface for viewing the recorded videos from the remote server
- [ ] Collecting additional vehicle data (speed, rpm, location)
- [ ] Objection detection?? (possibly using something like the depthAI OakD cam)
