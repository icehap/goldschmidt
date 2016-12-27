#! /usr/bin/env python3

"""
Read out some gaussmeter via USB connection
"""

import serial as s
import numpy as np
import time
import pylab as p
import seaborn as sb
import argparse

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

    def __init__(self, port="/dev/ttyUSB0"):
        """
        Constructor needs read and write access to 
        the port
        """
        self.meter = s.Serial(port) # default settings are ok
        self.unit = None
        print ("Meter initialized")

    def measure(self, npoints, interval):
        """
        Make a measurement with npoints each interval seconds
    
        Args:
            npoints (int): number of measurement points
            interval (int): make a measurement each interval seconds
            
        Keyword Args:
            silent (bool): Suppress output

        """
        # find out unit
        time.sleep(3)
        some_data = self.meter.read_all()
        some_data = some_data.split(b"\r")[0]
        self.unit = None
        while self.unit is None:
            try:
                self.unit = get_unit(some_data)
            except ValueError:
                print ("Can not get unit, trying again...")
                time.sleep(5)
                some_data = self.meter.read_all()
                some_data = some_data.split(b"\r")[0]
        print ("All data will be in {}".format(self.unit))
            
        for n in range(npoints):
            data = self.meter.read_all()
            field = decode_meter_output(data)
            field = field.mean()
            time.sleep(interval)
            yield n*interval, field        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(usage="magnetometer.py OPTIONS \n\nUse a MilliGaussMeter GU-3001D. The script might require root privileges to access /dev/ttyUSB0 (can be avoided by setting a udev rule" )
    parser.add_argument("--npoints", help="measure n points each interval seconds",
                        default=100000, type=int)
    parser.add_argument("--interval", help="average over this measurement time",
                        default=5, type=int)
    parser.add_argument("--silent", help="suppres output",
                        default=False, action="store_true")
    

    args = parser.parse_args()
    meter = GaussMeterGU3001D()
    for seconds, fields in meter.measure(args.npoints, args.interval):
        if not args.silent:
            print (seconds, fields)

 
