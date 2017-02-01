# goldschmidt
Read out a DU-3001D Milli-Gauss meter from Lutron or the Lutron TM-947SD thermometer

## Requirements:

* python3

* tkinter

In Ubuntu, the usual way how it is done is that `/dev/ttyUSB0` is only accesible with root privileges. To avoid that copy

`ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", OWNER=="USER"` where USER is replaced by the actual user

to a file `goldschmidt.rules` and put it in `/etc/udev/rules.d/`

##  Setup

`sudo pip3 install goldschmidt`

## Usage

Run it with `goldschmidt` from the terminal
