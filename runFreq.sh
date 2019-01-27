#!/bin/bash

cd /home/pi/FreqGen;
python freqgen.py >/dev/null 2>&1
sudo shutdown --no-wall now

