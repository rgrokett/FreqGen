"""
FreqGen - Generate RF signals using the F5OEO rpitx package and
    a raspberry pi.
    This version provides a OLED LCD display with control buttons
    and battery powered raspberry pi zero for a portable RF signal 
    generator.

Original RPITX code from (and great THANKS to):
https://github.com/F5OEO/rpitx

Version 1.0 2019.01.15 - r.grokett initial
Version 1.1 2019.06-28 - removed tabs

License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html

"""

import os, sys
import subprocess
import time
import json

from gpiozero import Button
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont, Image


# USER EDITABLE
DEBUG = 0   # 0/1 = off/on
version = 1.0   # Software version
freq = 434.0    # Starting Frequency in Mhz

# I2C interface and address
serial = i2c(port=1, address=0x3C)
# OLED Device
device = sh1106(serial)

# GPIO PINS 
bt = None   # gpiozero bounce time is buggy! leave 'None'
BTN1 = Button(23,bounce_time=bt)    # Next
BTN2 = Button(24,bounce_time=bt)    # Prev
BTN3 = Button(25,bounce_time=bt)    # Select

# Frequency display digits and range
digits = [ '_','0','1','2','3','4','5','6','7','8','9','.' ]
f_range= [ 0.05, 1500.0 ]
stats = [ 'Idle','Active' ]

# Load JSON list of RPITX modules
with open('freqgen.json') as json_data:
    txjson = json.load(json_data,)
path = txjson['RPITX_PATH']
modes = [] 
for item in txjson['modulations']:
    modes.append(item['name'])

if DEBUG:
    print( "DEBUG: 1" )
    print( "RPITX Path:"+path )
    print( "Modes:" )
    print( modes )

# Display Defaults
title_txt = "FreqGen    v"+str(version)
mode = modes[0]
stat = stats[0]
sel_txt = ">"
message = "Quit"

# Use custom font
font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
    'fonts', 'C&C Red Alert [INET].ttf'))
font2 = ImageFont.truetype(font_path, 12)

# Splash Screen
img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        'images', 'freqgen_icon.png'))
logo = Image.open(img_path).convert("RGBA")
background = Image.new("RGBA", device.size, "black")
posn = ((device.width - logo.width) // 2, 0)
background.paste(logo, posn)


##################
# Methods
##################

# Menu Selection
def update_menu(selected):
    if DEBUG:
        print ("update_menu()")
    # Update Screen Text
    freq_txt = "FREQ: "+str(freq)+" mhz"
    mode_txt = "MODE: "+str(mode)
    stat_txt = "STAT: "+str(stat)
    msgs_txt = str(message)
    # Set menu item selection
    if selected > -1:
        y = 15 + (10 * selected)
    else:
        y = 35
    # Update the display
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((15,5), title_txt, fill="white")
        draw.text((15,15), freq_txt, font=font2, fill="white")
        draw.text((15,25), mode_txt, font=font2, fill="white")
        draw.text((15,35), stat_txt, font=font2, fill="white")
        draw.text((15,45), msgs_txt, font=font2, fill="white")
        draw.text((10,y), sel_txt, font=font2, fill="white")

# Menu Selection
def select_menu(selected):
    if DEBUG:
        print ("select_menu()")

    loaded = 0
    while not loaded:
      if BTN1.is_pressed: 
        selected = selected - 1
        if selected < 0:
            selected = 0
        update_menu(selected)       
        BTN2.wait_for_release()
      if BTN2.is_pressed: 
        selected = selected + 1
        if selected > 3:
            selected = 3
        update_menu(selected)       
        BTN1.wait_for_release()
      if BTN3.is_pressed: 
        loaded = 1
        BTN3.wait_for_release()
      time.sleep(0.1)

    return(selected)


# Frequency Entry
def change_freq(freq):
    # Display current Freq
    if DEBUG:
        print ("change_freq()")
        print ("Current Freq: "+str(freq)+" mhz")

    l_freq = list(' '+str(freq))
    loaded = 0
    clr_freq = 1
    press_cnt = 0
    next_digit = 0
    digit = 0
    btn3_twice = 0
    stat_txt = ''
    max = 11
    min = 1
    while not loaded:
        # Update the display
        with canvas(device) as draw:
          if BTN1.is_pressed:
            if clr_freq :
                clr_freq = 0
                del l_freq[:]
                press_cnt = 0
                next_digit = 1
                digit = 0
                stat_txt = ''
            press_cnt = press_cnt + 1
            btn3_twice = 0
            if press_cnt > max:
                press_cnt = max
            BTN1.wait_for_release()
          if BTN2.is_pressed:
            if clr_freq :
                clr_freq = 0
                del l_freq[:]
                press_cnt = 2
                next_digit = 1
                digit = 0
                stat_txt = ''
            press_cnt = press_cnt - 1
            btn3_twice = 0
            if press_cnt < min:
                press_cnt = min
            BTN2.wait_for_release()
          if BTN3.is_pressed:
            btn3_twice = btn3_twice + 1
            if btn3_twice > 1:
                l_freq.pop()
                freq = float(''.join(l_freq))
                loaded = 1
                if freq < f_range[0] or freq > f_range[1]:
                    stat_txt = "OUT OF RANGE"
                    loaded = 0
                    clr_freq = 1
            else:
                if press_cnt == 11: # only one decimal pt .
                    max = max - 1 
                next_digit = 1
                digit = digit + 1
                press_cnt = 0

            BTN3.wait_for_release()
          # DISPLAY FREQ DIGITS
          if next_digit:
            l_freq.append(digits[press_cnt])
            next_digit = 0
          elif press_cnt > 0: 
            l_freq[digit] = digits[press_cnt]

          s_freq = str(''.join(l_freq))
          draw.rectangle(device.bounding_box, outline="white", fill="black")
          draw.text((15,5), 'Enter Frequency:', fill="white")
          draw.text((15,15), '(0.005 - 1500.0 mhz)', font=font2,fill="white")
          draw.text((15,35), s_freq, font=font2,fill="white")
          draw.text((15,45), stat_txt, font=font2,fill="white")
          draw.text((10,35), sel_txt, font=font2,fill="white")

          time.sleep(0.1)

    if DEBUG:
        print ("New Freq: "+str(freq)+" mhz")
    return(freq)    

# Return modulation attributes
def select_mode(mode):
    if DEBUG:
        print ("select_mode()")
    min = 0
    max = len(modes) - 1
    mode_num = min
    # Display three modes (prev, cur, next)
    while 1:
        if BTN1.is_pressed:
            mode_num = mode_num - 1
            if mode_num < min:
                    mode_num = min
            BTN1.wait_for_release()
        if BTN2.is_pressed:
            mode_num = mode_num + 1
            if mode_num > max:
                    mode_num = max
            BTN2.wait_for_release()
        if BTN3.is_pressed:
            mode = modes[mode_num]
            BTN3.wait_for_release()
            break
        # Update the display
        # Shows 3 modes at a time
        if (mode_num - 1) < 0:
            mode_prev_txt = " "
        else:
            mode_prev_txt = modes[mode_num-1]
        if (mode_num + 1) > max:
            mode_next_txt = " "
        else:
            mode_next_txt = modes[mode_num+1]
        mode_curr_txt = ">"+modes[mode_num]
        # Update the display
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((15,5), 'Select Mode:', fill="white")
            draw.text((15,15), mode_prev_txt, font=font2,fill="white")
            draw.text((15,25), mode_curr_txt, font=font2,fill="white")
            draw.text((15,35), mode_next_txt, font=font2,fill="white")
        time.sleep(0.1)
    return(mode)

# Return modulation attributes
def get_txattrs(modulation):
    if DEBUG:
        print ("get_txtattrs("+modulation+")")
    txattrs = []
    for item in txjson['modulations']:
        if item['name'] == modulation:
            txattrs = item
    return(txattrs)

# EXECUTE RPITX Program
def execute_pgm(mode, freq):
    if DEBUG:
        print ("execute_pgm()")
    stop_all()  # Be sure no TX is running
    item = get_txattrs(mode)
    shell = item['shell']
    ext = item['freq']
    cmd = "cd "+path+"; ./"+shell+" "+str(freq)+str(ext)+" >/dev/null 2>/dev/null &"
    os.system(cmd)
    if DEBUG:
        print (cmd)
    update_menu(-1)     
    BTN3.wait_for_press()
    BTN3.wait_for_release()
    time.sleep(0.1)


# KILL TRANSMISSION
def stop_all():
    if DEBUG:
        print ("stop_all()")
    for item in txjson['modulations']:
        cmd = "sudo killall "+item['command']+" "+item['shell']+">/dev/null 2>&1"
        os.system(cmd)
        if DEBUG: 
            print (cmd)

# VERIFY EXIT
def verify_exit():
    if DEBUG:
        print ("verify_exit()")

    loaded = 0
    selected = 0
    while not loaded:
      if BTN1.is_pressed: 
        selected = selected - 1
        if selected < 0:
            selected = 0
        BTN2.wait_for_release()
      if BTN2.is_pressed: 
        selected = selected + 1
        if selected > 1:
            selected = 1
        BTN1.wait_for_release()
      if BTN3.is_pressed: 
        loaded = 1
        BTN3.wait_for_release()

      # Update the display
      y = 15 + (10 * selected)
      with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((15,5), 'Exit?', fill="white")
        draw.text((15,15), 'CANCEL', font=font2,fill="white")
        draw.text((15,25), 'EXIT', font=font2,fill="white")
        draw.text((10,y), sel_txt, font=font2, fill="white")
      time.sleep(0.1)

    return(selected)

##################

    
##################
# MAIN LOOP 
##################
if DEBUG:
    print ("Starting...")

# STARTUP SCREEN
device.display(background.convert(device.mode))
time.sleep(2)


# Main Menu with default values
update_menu(0)
selected = 0

while 1:
    # Menu Selection
    message = "Quit"
    selection = select_menu(selected)
    if DEBUG:
        print ("Got selection = "+str(selection))
    if selection == 0:
        # Frequency change
        freq = change_freq(freq)
        update_menu(0)
        selected = 0
    elif selection == 1:
        # Mode selection 
        mode = select_mode(mode)
        update_menu(2)
        selected = 2
    elif selection == 2:
        stat = 'ACTIVE' 
        message = "Press Select to Stop"
        update_menu(2)
        execute_pgm(mode, freq)
        stop_all()
        stat = 'IDLE'   
        message = "Quit"
        update_menu(0)
        selected = 0
    elif selection == 3:
        selected = verify_exit()
        if selected:
          quit()
        update_menu(0)
    if DEBUG :
        print ('Loop')

    time.sleep(0.2)

# END LOOP 


