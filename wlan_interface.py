#!/usr/bin/python
import commands
import os
import sys


class TempWorkingDir(object):
  """Context-manager to change the current working directory."""

  def __init__(self, new_path):
    self.new_path = new_path
    self.root_dir = os.getcwd()

  def __enter__(self):
    os.chdir(self.new_path)

  def __exit__(self, *args):
    os.chdir(self.root_dir)


def run_command(command):
  _, output = commands.getstatusoutput(command)
  return output

user = run_command("whoami")
if user != "root":
    raise ValueError("must run script as root")


if len(sys.argv) < 2:
    raise ValueError("expected input parameter: dongle|pi")

filter_to = sys.argv[1]

CACHE_BASE = "/dev/shm/cached_wlan_interface_%s"
cache_key = CACHE_BASE % filter_to

try:
    with open(cache_key, "rb") as f:
        contents = f.read()
        print contents
        sys.exit(0)
except IOError:
    # cached value does not exist yet
    pass

PI_WIFI_DRIVER = "brcmfmac" 
output = run_command("airmon-ng")
lines = output.splitlines()
interfaces = [l for l in lines if l.startswith("phy")]

def isolate_builtin_wifi_int(interfaces):
    for iface in interfaces:
        tokens = iface.split()
        driver = tokens[2]
        if driver == PI_WIFI_DRIVER:
            return iface
    raise ValueError("could not find builtin pi interface, maybe it was disabled")


def wlan_from_int(interface):
    tokens = interface.split()
    wlan = tokens[1]
    return wlan


def first_interface_not_wlan(interfaces, not_this_wlan):
    for iface in interfaces:
        tokens = iface.split()
        wlan = tokens[1]
        if wlan != not_this_wlan:
            return iface
    raise ValueError("only pi wlan is visible; is dongle plugged in?")

pi_wifi_interface = isolate_builtin_wifi_int(interfaces)
pi_wlan = wlan_from_int(pi_wifi_interface)

dongle_wifi_interface = first_interface_not_wlan(interfaces, pi_wlan)
dongle_wlan = wlan_from_int(dongle_wifi_interface)

if filter_to != "dongle" and filter_to != "pi":
    raise ValueError("input should be: dongle|pi")

if filter_to == "dongle":
    print dongle_wlan
else:
    print pi_wlan

with open(CACHE_BASE % "dongle", "w+") as f:
    f.write(dongle_wlan)
with open(CACHE_BASE % "pi", "w+") as f:
    f.write(pi_wlan)
