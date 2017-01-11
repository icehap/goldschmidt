"""
Read out some gaussmeter via USB connection
"""

import serial as s
import numpy as np
import time
import pylab as p
import seaborn as sb
import argparse

try:
    import zmq
except ImportError:
    print("Can not import zero MQ")

from . import get_logger

# example word... \r\x0241B20200000052\

# Connection settings:
# Baud rate 9600 
# Parity  No parity
# Data bit no. 8 Data bits
# Stop bit  1 Stop 
#

def save_execute(func):
    """
    Calls func with args, kwargs and 
    returns nan when func raises a value error
    
    FIXME: treatment of the errors!
    """
    def wrap_f(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except ValueError:
            return np.nan
    return wrap_f


#@save_execute
def decode_fields(data):
    """
    Give meaning to the fields of a 16 byte
    word returned by the meter. Words are 
    separated by \r

    Args:
        data (bytes): A single word of length 16 
                      
    """
    #### from the manual...
    # http://www.sunwe.com.tw/lutron/GU-3001eop.pdf
    # The 16 digits data stream will be displayed in the
    # following  format :
    # D15 D14 D13 D12 D11 D10 D9 D8 D7 D6 D5 D4 D3 D2 D1 D0
    # Each digit indicates the following status :
    # D15  Start Word = 02
    # D14  4
    # D13  When send the upper display data = 1
    #      When send the lower display data = 2
    # D12 & Annunciator for Display
    # D11   mG = B3
    #       uT = B2
    # D10 Polarity 
    #       0 = Positive
    #       1 = Negative
    # D9  Decimal Point(DP), position from right to the
    #       left, 0 = No DP, 1= 1 DP, 2 = 2 DP, 3 = 3 DP
    # D8 to D1  Display reading, D8 = MSD, D1 = LSD
    #           For example : 
    #           If the display reading is 1234, then D8 to
    #           D1 is : 00001234
    #          D0 End Word = 0D

    if not len(data) == 15:
        return np.nan
    polarity = data[5:6].decode()
    decimal_point = data[6:7].decode()
    mg_data = data[7:15].decode()
    polarity = int(polarity)
    decimal_point = int(decimal_point)
    if polarity:
        polarity = -1
    else:
        polarity = 1
    if decimal_point:
        index = -1*int(decimal_point)
        mg_data = mg_data[:index] + "." + mg_data[index:]
    mg_data = polarity*float(mg_data)
    return mg_data


def get_unit(data):
    """
    Get the unit from a magnetometer word
    """
    if not len(data) == 15:
        raise ValueError("Data corrupted!")
    unit = data[3:5].decode()    
    if unit == "B3":
        unit = "mG"
    elif unit == "B2":
        unit = "uT"
    else:
        raise ValueError("Unit not understood {}".format(unit))
    return unit 

def decode_meter_output(data):
    """
    Decode the bytestring with 
    hex numbers to the field 
    information
    
    Args:
        data (bytes): raw output from serial port

    """
    data = data.split(b"\r")
    data = [decode_fields(word) for word in data]
    data = np.array(data)
    data = data[np.isfinite(data)]
    return data


class GaussMeterGU3001D(object):
    """
    The named instrument
    """

    def __init__(self, device="/dev/ttyUSB0", loglevel=20,\
                 publish=False, port=9876):
        """
        Constructor needs read and write access to 
        the port

        Keyword Args:
            port (str): The virtual serial connection on a UNIX system
            loglevel (int): 10: debug, 20: info, 30: warnlng....
            publish (bool): publish data on port
            port (int): use this port if publish = True
        """
        self.meter = s.Serial(device) # default settings are ok
        self.logger = get_logger(loglevel)
        self.logger.debug("Meter initialized")
        self.publish = publish
        self.port = port
        self._socket = None

    def _setup_port(self):
        """
        Setup the port for publishing

        Returns:
            None
        """
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        self._socket.bind("tcp://0.0.0.0:%s" % int(self.port))
        return

    @property
    def unit(self):
        """
        Figure out the units of the meter
        """
        time.sleep(1)
        some_data = self.meter.read_all()
        some_data = some_data.split(b"\r")[0]
        unit = None
        while unit is None:
            try:
                unit = get_unit(some_data)
            except ValueError:
                self.logger.debug("Can not get unit from {}, trying again...".format(some_data))
                time.sleep(2)
                some_data = self.meter.read_all()
                some_data = some_data.split(b"\r")[0]
        self.logger.info("All data will be in {}".format(unit))
        return unit    

    def measure(self, measurement_time=2):
        """
        Measure a single point

        Keyword Args:
            measurement_time (int): average the values over the measurement time in seconds

        """
        time.sleep(measurement_time) # give the meter time to acquire some data
        data = self.meter.read_all()
        try:
            unit = get_unit(data.split(b"\r")[0])
        except ValueError:
            unit = "--"
        field = decode_meter_output(data)
        field = field.mean()
        if self.publish and (self._socket is None):
            self._setup_port()
        if self.publish:
            self._socket.send_string("{} {}; {}".format("GU3001D", field, unit))
        return field         

    def measure_continously(self, npoints, interval):
        """
        Make a measurement with npoints each interval seconds
    
        Args:
            npoints (int): number of measurement points
            interval (int): make a measurement each interval seconds
            
        Keyword Args:
            silent (bool): Suppress output

        """

        for n in range(npoints):
            field = self.measure(measurement_time=interval)
            yield n*interval, field        

 
