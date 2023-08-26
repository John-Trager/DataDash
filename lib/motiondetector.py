from lib.gps import GPS
from lib.utils import get_distance


class MotionDetector:
    def __init__(self, dist_threshold: float) -> None:
        """
        Args:
            dist_threshold(float): the threshold distance in meters of how close two points can be before considered in motion
        """
        self.gps = GPS()
        self.lagging_pos = None
        self.dist_threshold = dist_threshold

    def initialize(self):
        self.gps.initialize()

    def set_lagging_pos(self):
        recv = self.gps.get_coords()
        self.lagging_pos = [recv[1], recv[2]]

    def in_motion(self) -> bool:
        """
        can be used to check if the Datadash is in motion

        returns (bool): if gps lagging pos is within distance threshold of cur pos
        """
        recv = self.gps.get_coords()
        curr_pos = [recv[1], recv[2]]

        # if the lagging pos hasn't been set yet
        # use the current pos and retry later
        if self.lagging_pos == None:
            self.lagging_pos = curr_pos
            return True

        return get_distance(self.lagging_pos, curr_pos) >= self.dist_threshold
