#!/usr/bin/sh
systemctl stop dhcpcd.service
airmon-ng check kill

# the studo here is redundant but we'll try it out...
sudo ifconfig $(sudo /opt/eblimp/wlan_interface.py pi) down
sudo ifconfig $(sudo /opt/eblimp/wlan_interface.py dongle) down
sudo iw dev $(sudo /opt/eblimp/wlan_interface.py dongle) set monitor otherbss fcsfail
sudo ifconfig $(sudo /opt/eblimp/wlan_interface.py dongle) up
sudo iwconfig $(sudo /opt/eblimp/wlan_interface.py dongle) channel 13
