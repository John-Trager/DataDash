"""
This is the data uploader service
"""
import threading
import requests
import json
import os
from pathlib import Path
import time
from lib.utils import check_internet_conn, Timer


LOGNAME = "uploads.json"
FILETYPE = ".mp4"
UPLOADEDFILES = "uploaded_files"


class DataUploader:
    def __init__(
        self,
        server_url: str,
        src_data_path: str,
        log_path: str,
        loop_time: int,
        conn_timeout: int,
        overwrite_log: bool,
    ) -> None:
        """
        Initialize a new DataUploader instance.

        Args:
            server_url(str): url of the video storage server
            src_data_path (str): path to files to be uploaded
            log_path (str): path to logs used by the DataUploader
            loop_time (str): how often we want the uploader to check for new files (in seconds)
            conn_timeout (str): how long we want to wait between checking for internet connection
            overwrite_log (bool): overwrite the log to the default, this will remove the log of
                what files have been uploaded thus it make cause files to be re-uploaded
        """
        self.server_url = server_url
        self.src = src_data_path
        self.log_path = log_path
        self.loop_time = loop_time
        self.conn_timeout = conn_timeout

        self.end_flag = threading.Event()

        ## Handling the upload log setup

        # make sure we have the log dir
        if overwrite_log:
            print("Overwriting DataUploader log!")

        if (not os.path.exists(os.path.join(log_path, LOGNAME))) or overwrite_log:
            # if not, create the log path
            Path(log_path).mkdir(parents=True, exist_ok=True)

            # create the default log file
            default_log = {UPLOADEDFILES: []}

            with open(os.path.join(log_path, LOGNAME), "w") as json_file:
                json.dump(default_log, json_file, indent=4)

        # read in the log
        with open(os.path.join(log_path, LOGNAME), "r") as json_file:
            self.upload_log = json.load(json_file)

    def __del__(self) -> None:
        self.stop()

    def start(self):
        print("starting data uploader")
        upload_thread = threading.Thread(
            target=self.check_and_upload_files,
            args=(),
        )
        upload_thread.start()

    def stop(self):
        self.end_flag.set()

    def check_and_upload_files(self):
        while not self.end_flag.is_set():
            # attempt to connect to the internet
            # and wait until end_flag is set or we actually make a connection
            # to the internet
            if not self.connect_to_internet():
                break

            timer = Timer()

            # read json file
            with open(os.path.join(self.log_path, LOGNAME), "r") as json_file:
                self.upload_log = json.load(json_file)

            # read what files exist in src_data_path
            # and that have not yet been uploaded
            # TODO: consider removing the files that have been uploaded
            not_uploaded_files = [
                file_name
                for file_name in os.listdir(self.src)
                if file_name.endswith(FILETYPE)
                and file_name not in self.upload_log[UPLOADEDFILES]
            ]

            for file_name in not_uploaded_files:
                try:
                    self.upload_file(file_name)
                    self.upload_log[UPLOADEDFILES].append(file_name)
                    self.write_upload_dict_to_json()
                except Exception as e:
                    print(f"Error uploading file: {e}")
                    print(f"sleeping for {self.conn_timeout}")
                    time.sleep(self.conn_timeout)

            # handle loop sleeping time
            time.sleep(max(0, self.loop_time - timer.elapsed()))

    def upload_file(self, filename):
        file_path = os.path.join(self.src, filename)
        print(f"Moving file {file_path} to server...")

        with open(file_path, "rb") as file:
            response = requests.post(self.server_url, files={"file": file})

            if response.status_code == 200:
                print("*DONE*")
                return
            else:
                raise Exception(
                    f"An error occurred when attempting to upload a file.\
                      Request status: {response.text},\
                      Request text: {response.status_code}"
                )

    def dummy_upload_file(self, filename):
        src = os.path.join(self.src, filename)
        print(f"Moving file {src} to DUMMY")
        time.sleep(1)

    def write_upload_dict_to_json(self):
        with open(os.path.join(self.log_path, LOGNAME), "w") as json_file:
            json.dump(self.upload_log, json_file, indent=4)

    def connect_to_internet(self) -> bool:
        """
        Checks connection to the internet, if we are not connected
        we will wait `self.conn_timeout` seconds and try again.

        The method will be stopped when `self.end_flag` is set or
        if we make a connection with the internet successfully

        returns: if connected to the internet
        """
        while not self.end_flag.is_set():
            if check_internet_conn:
                return True
            else:
                print(f"No internet connection sleeping for {self.conn_timeout}...")
                time.sleep(self.conn_timeout)

        return False
