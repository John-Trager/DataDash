# DataDash
The goal of this project is to collect data from a cars dash cam and upload it to the cloud or remote storage once connected to wifi.

## Hardware
The device is made up of:
- 2 Raspberry PIs (one for the recording device, 1 for the remote video storage)
- logitech USB webcam
- Adafruit MPU/IMU 6050

I have also experimented with a simple GPS module that I had but due to its long-wait time in acquiring satelites it is currently not in use. I have also thought about using a "elm327 obdii bluetooth adapter" to read data directly from the vehicle we are in (such as speed, rpm, etc) but this is a work in progress.

## Implementation
<i>in progress</i>

## What's Next
- [x] Working device
    - motion sensor, camera, and basic state machine working
- [ ] Further testing the device in the field
- [ ] Web interface for viewing the recorded videos from the remote server
- [ ] Collecting additional vehicle data (speed, rpm, location)

## DataDash System State
> [!Note]
> this is still being built out

- script that runs on startup
    - :idle: sits in the idle state until motion is detected
        - if in the idle state for longer than X minutes, GOTO :done:
        - once motion is detected GOTO :in-motion:
    - :in-motion: once motion is detected record video
        - once motion is no longer detected GOTO :wait-for-upload: 
    - :wait-for-upload: try to connect to server to upload data
        - if no connection is made to upload server for X minutes, GOTO :idle:
        - once connection to server is established GOTO :upload-state:
    - :upload-state: upload data to server
        - once no more data to upload GOTO :idle:
        - if connection to server is broken GOTO :wait-for-upload:
        - if fatal error GOTO :done:
            - something like authentication to server fails...
    - :done: the end state for the device 

[//]: # (TODO: create state diagram somehow)


## Dev Info

- https://www.thequantizer.com/access-raspberry-pi-remotely/#gadget-mode-ssh-over-usb
    - gadget mode for raspi so we can access from computer in the field when no networks are around