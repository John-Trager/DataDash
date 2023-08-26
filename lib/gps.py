"""
a GPS class for the Adafruit ultimate gps v3
"""

import serial
import pynmea2 as nmea
from math import atan2, cos, sin, degrees, radians
import time


class GPS:
    def __init__(self, baudrate=9600, _timeout=None, dirr="/dev/ttyUSB0", rate=5):
        """
        TODO: allow rate to be changed (not working currently)
        rate: the rate of the gps response in HZ (max 5 hz tested, possible 10hz if only receiving minimal data)
        """
        try:
            self.stream = serial.Serial(dirr, baudrate, timeout=_timeout)
            self.rate = rate

        except serial.SerialException as e:
            print("GPS device may not be plugged in!")
            print("Device serial comm error: {}".format(e))
            exit(1)

    def initialize(self):
        """
        loop until gps has satellite fix
        :returns: True when fix is achieved
        :returns: False if there is an error or if skipped
        :gps_qual: 0 connection, 1 regular gps, 2 dgps
        additionally configures gps update frequency and what data we receive
        """
        # ___ we can send commands here for gps configuration ___

        # TODO: we likely only want GGA or RMC if HZ is at 10 also test this
        # Turn on the basic GGA and RMC info (what we typically want)
        self.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

        # set gps update rate. milli is the millisecond delay between updates
        # TODO: fix byte string .format errors so we can use self.rate
        self.send_command(b"PMTK220,200")
        # self.send_command(b"PMTK220,{milli}".format(milli=int(1.0/self.rate * 1000)))

        # enable WAAS mode for DGPS
        self.send_command(b"PMTK301,2")  # PMTK_API_SET_DGPS_MODE
        self.send_command(
            b"PMTK501,2"
        )  # PMTK_API_DT_DGPS_MODE (TODO:unsure if needed - or even what it does)

        # enable SBAS
        self.send_command(b"PMTK313,1")  # PMTK_API_SET_SBAS_ENABLED
        self.send_command(
            b"PMTK513,1"
        )  # PMTK_DT_SBAS_ENABLED (TODO:unsure if needed - or even what it does)

        num_sats = 0
        gps_qual = 0
        while gps_qual != 2:  # only accept DGPS
            try:
                sentence = self.stream.readline().decode()
                if sentence.find("GGA") > 0:
                    data = nmea.parse(sentence)
                    num_sats = int(data.num_sats)
                    gps_qual = int(data.gps_qual)
                    print(
                        "\rnumber of sats: "
                        + str(num_sats)
                        + " gps qual: "
                        + str(gps_qual),
                        end="",
                    )
            except KeyboardInterrupt:
                return False

            except nmea.ParseError as e:
                print("Nmea parse error: {}".format(e))
                continue

            except UnicodeDecodeError as e:
                print("Decode error: {}".format(e))
                continue

            except serial.SerialException as e:
                print("\r" + "Device serial comm error: {}".format(e), end="")
                continue

        return True

    def start(self):
        # TODO
        # currently doesn't do anything
        pass

    def stop(self):
        """
        closes gps stream
        """
        self.stream.close()

    def get_coords(self):
        """
        returns [timestamp (UTC?), latitude, longitude, gps quality]
        timestamp: seems to be on time of device?
        """
        try:
            sentence = self.stream.readline().decode()
            if sentence.find("GGA") > 0:
                data = nmea.parse(sentence)
                return data.timestamp, data.latitude, data.longitude, data.gps_qual

        except nmea.ParseError as e:
            print("Parse error: {}".format(e))
            raise Exception

        except serial.SerialException as e:
            print("Device error: {}".format(e))
            raise Exception

    def process_coords(self, gps_loc, time_stamp, gps_heading):
        """
        TODO: TEST HEADING
        constantly updates gps location [lat,lon] with a time_stamp of the reading
        gps_loc: [latitide,longitude] both double precision
        time stamp: time in seconds since jan 1 1970 (depends on system though) double precision
        """
        try:
            while True:
                sentence = self.stream.readline().decode()
                if sentence.find("GGA") > 0:
                    # get gps nmea sentence
                    data = nmea.parse(sentence)
                    # if gps has changed update it
                    if gps_loc[0] != data.latitude or gps_loc[1] != data.longitude:
                        # get time stamp, time in seconds since jan 1 1970 (depends on system though)
                        time_stamp.value = time.time()
                        # update heading (formula from: https://gis.stackexchange.com/questions/228656/finding-compass-direction-between-two-distant-gps-points)
                        y = cos(radians(data.latitude)) * sin(
                            radians(data.longitude - gps_loc[1])
                        )
                        x = cos(radians(gps_loc[0])) * sin(
                            radians(data.latitude)
                        ) - sin(radians(gps_loc[0])) * cos(
                            radians(data.latitude)
                        ) * cos(
                            radians(data.longitude - gps_loc[1])
                        )
                        gps_heading.value = degrees(atan2(y, x))
                        # update gps location
                        gps_loc[0] = data.latitude
                        gps_loc[1] = data.longitude

        except KeyboardInterrupt:
            print("gps shutting down")
            return

        except Exception as e:
            print("error in parsing gps: {}".format(e))

    def get_sentence(self):
        """
        get sentence from gps
        """
        return self.stream.readline().decode()

    def send_command(self, command, add_checksum=True):
        """
        send a command to the gps over serial
        """
        self.stream.write(b"$")
        self.stream.write(command)
        if add_checksum:
            checksum = 0
            for char in command:
                checksum ^= char
            self.stream.write(b"*")
            self.stream.write(bytes("{:02x}".format(checksum).upper(), "ascii"))
        self.stream.write(b"\r\n")
