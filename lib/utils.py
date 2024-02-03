from lib.params import DEBUG
from datetime import datetime
import numpy as np
import json
import os
import paramiko
import time

SERVER_HOST = "server1.local"


### server functions ###
def server_reachable(hostname: str = SERVER_HOST) -> bool:
    """Pings server to see if it is reachable"""
    # this will only work on unix systems
    response = os.system("ping -c 1 " + hostname + " > /dev/null")
    return response == 0


def get_server_conn(config_path: str = "config/server.json"):
    """
    Connect to the server using the details in config_path

    :param config_path: path to the server config file
    :return: paramiko.SSHClient
    """

    # check if config_path exists
    if not os.path.exists(config_path):
        log_error(f"Config file not found at {config_path}")
        exit(1)

    config = {}
    with open(config_path) as f:
        config = json.load(f)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        config["hostname"], config["port"], config["username"], config["password"]
    )
    log("Connected to server")
    return client



### More general util functions ###
def get_string_time_now() -> str:
    """Returns the current time in string format"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log(*args):
    """Logs a message to the console with timestamp"""
    # color the timestamp
    timestamp = get_string_time_now()
    timestamp = f"\033[92m[{timestamp}]\033[0m"
    print(f"{timestamp} " + " ".join(map(str, args)), flush=True)


def log_warn(*args):
    """Logs a warning message to the console with timestamp"""
    timestamp = get_string_time_now()
    timestamp = f"\033[33m[{timestamp}] Warning:\033[0m"
    print(f"{timestamp} " + " ".join(map(str, args)), flush=True)


def log_error(*args):
    """Logs an error message to the console with timestamp"""
    # color the timestamp red
    timestamp = get_string_time_now()
    timestamp = f"\033[91m[{timestamp}] Error:\033[0m"
    print(f"{timestamp} " + " ".join(map(str, args)), flush=True)


def log_debug(*args):
    """Logs a debug message to the console with timestamp"""
    # color the timestamp blue
    if DEBUG:
        timestamp = get_string_time_now()
        timestamp = f"\033[94m[{timestamp}] Debug:\033[0m"
        print(f"{timestamp} " + " ".join(map(str, args)), flush=True)

class Timer:
    """
    A simple timer class that easly calculates elapsed time
    """
    def __init__(self) -> None:
        self.start = time.time()

    def elapsed(self) -> float:
        return max(0, time.time() - self.start)

class RollingVarianceCalculator:
    """
    Calculates the rolling variance based on a window size

    Args:
        window_size(int): how many data points to consider in the variance window
    """
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.data = []
        self.variance = None

    def update(self, new_value):
        # TODO: make this more efficient, naive algo at the moment
        # since var is calculated every update in full there may be a better method
        self.data.append(new_value)
        if len(self.data) > self.window_size:
            self.data.pop(0)
        if len(self.data) >= self.window_size:
            window = np.array(self.data[-self.window_size :])
            self.variance = np.var(window)

    def reset(self):
        '''resets the RVCs buffer'''
        self.variance = None
        self.data = []