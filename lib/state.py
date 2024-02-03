"""
states for the datadash state machine
"""

from enum import Enum


class State(Enum):
    START = 1
    IDLE = 2
    IN_MOTION = 3
    WAIT_FOR_UPLOAD = 4
    UPLOAD_STATE = 5
    DONE = 6
