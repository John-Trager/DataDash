# DashData
The goal of this project is to collect data from a cars dash cam and upload it to the cloud or remote storage once connected to wifi.


## Implementation

there will be a `main.py` file that starts the data recorder and data uploaded services using cron

- Data Recorder: Records camera data (+ other possible data) and stores on disk
- Data Uploader: Keeps track of what files have been uploaded and uploads data when a network is available

TODO: how to determine when to shutdown
- if the raspi detects that we haven't moved in X amount of time start the shutdown sequence (stop recording, last check for network, if not available shutdown)
    - we can either use the GPS (which I have some existing code for) or use the IMU?