#!/bin/bash
#!/bin/bash

echo "Installing dependencies..."
sudo apt update
sudo apt upgrade

sudo apt install -y i2c-tools

sudo apt install -y git
sudo apt install -y python-dev python-pip
sudo apt install -y libfreetype6-dev libjpeg-dev build-essential
sudo apt install -y python-gpiozero
sudo apt install -y python-imaging python-smbus
sudo -H pip install --upgrade luma.oled --no-cache-dir

echo "OLED installed. Reboot to execute."
exit 0

