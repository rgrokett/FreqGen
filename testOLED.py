"""
Test SH1106 OLED 

Using lumaOLED Library
https://github.com/rm-hull/luma.oled

Version 1.0 2019.01.15 - r.grokett initial

License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html


"""

import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106


# I2C interface and address
serial = i2c(port=1, address=0x3C)
# OLED Device
device = sh1106(serial)

print ("Test for OLED Screen Starting...")

# STARTUP SCREEN
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 10), "Testing OLED", fill="white")
    draw.text((30, 30), "Hello World!", fill="white")

print ("You should see test message now for 5 seconds.")
time.sleep(5)

# Screen blanks automatically at end of program running
print ("The screen should be blank again.")
print ("Finished test.")


