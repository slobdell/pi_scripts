#!/usr/bin/python
import commands
import os
import sys

TO_PRODUCTIONIZE = [
    "/home/eblimp/projects/does_not_exist",
    "/home/eblimp/projects/led_controller",
    "/home/eblimp/projects/text_movie_gen",
]

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


def last_token(path):
    return path.split("/")[-1]

finished = []

for path in TO_PRODUCTIONIZE:
    try:
        with TempWorkingDir(path):
            run_command("make productionize")
        print "Finished compiling %s" % path
        dest = os.path.join("/opt/eblimp", last_token(path))
        created_src = os.path.join(path, "prod")
        cmd = "cp -r %s %s" % (created_src, dest)
        print "Removing any old copies of %s" % dest
        run_command("rm -rf %s" % dest)
        print "Copying from %s to %s" % (created_src, dest)
        run_command("cp -r %s %s" % (created_src, dest))
        finished.append(dest)
    except OSError:
        print "Directory %s does not exist, skipping" % path


print "Finished. Now update /etc/rc.local to launch scripts in locations:\n%s" % "\n".join(finished)
