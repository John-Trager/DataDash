import socket
import time
from math import radians, cos, sin, sqrt, asin
import numpy as np


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
        self.data.append(new_value)
        if len(self.data) > self.window_size:
            self.data.pop(0)
        if len(self.data) >= self.window_size:
            window = np.array(self.data[-self.window_size :])
            self.variance = np.var(window)


def check_internet_conn(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False
