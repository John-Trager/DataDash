import socket
import time
from math import radians, cos, sin, sqrt, asin
import numpy as np


class Timer:
    def __init__(self) -> None:
        self.start = time.time()

    def elapsed(self) -> float:
        return max(0, time.time() - self.start)


class RollingVarianceCalculator:
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


def get_distance(coord1: [float, float], coord2: [float, float]):
    """
    returns the distance in meters between two gps coordinate points
    """
    R = 6372.8
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi_1 = radians(lat1)
    phi_2 = radians(lat2)

    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = (
        sin(delta_phi / 2.0) ** 2
        + cos(phi_1) * cos(phi_2) * sin(delta_lambda / 2.0) ** 2
    )
    # c = 2*atan2(sqrt(a),sqrt(1-a))
    c = 2 * asin(sqrt(a))

    return R * c * 1000
