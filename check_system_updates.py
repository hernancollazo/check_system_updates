#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# It's a simple Nagios plugin to check using YUM/apt for package updates. 
# Auto-detect linux distribution, no configuration needed.
#
# Copyright (C) 2015 Hernan Collazo <hernan.collazo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
#

__title__ = "check_system_updates"
__version__ = "0.5b"

import os
import sys
import platform
import signal

OLD_PYTHON = False

# Nagios Status Codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

try:
    from subprocess import Popen, PIPE, STDOUT
except ImportError:
    OLD_PYTHON = True
    import commands


def runCmd(cmd):
    "Runs a system command and returns statuscode/output"
    if OLD_PYTHON:
        returncode, stdout = commands.getstatusoutput(cmd)
        if returncode >= 256:
            returncode = returncode / 256
    else:
        try:
            process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        except OSError, error:
            error = str(error)
            if error == "No such file or directory":
                end(UNKNOWN, "Cannot find utility '%s'" % cmd.split()[0])
            end(UNKNOWN, "Error trying to run utility '%s' - %s" % (cmd.split()[0], error))
        output = process.communicate()
        returncode = process.returncode
        stdout = output[0]
    if stdout is None or stdout == "":
        print("No output from command!")
    else:
        output = str(stdout).split("\n")
    return(returncode, output)


def osData():
    "Return OS information"
    myPlatform = platform.linux_distribution()
    osData = {}
    osData['system'] = platform.system()
    osData['dist'] = myPlatform[0]
    osData['version'] = myPlatform[1]
    osData['release'] = myPlatform[2]
    return osData


def checkUpdates(dist):
    "Return pending updates, based on linux-distribution"
    dist = dist.lower()
    if dist == 'centos':
        updates = yumUpdates()
    elif dist == 'ubuntu' or dist == 'debian':
        updates = aptUpdates()
    else:
        updates = "Unknown"
    return updates


def aptUpdates():
    "Get pending system updates using apt-get"
    cmdUpdate = "/usr/bin/apt-get -s dist-upgrade"
    cmdStatus, cmdOutput = runCmd(cmdUpdate)
    cmdOutput = ' '.join(cmdOutput)
    pendingUpdates = cmdOutput.count('Inst ')
    if pendingUpdates == 0:
        print("OK - No pending updates.")
        sys.exit(OK)
    elif pendingUpdates > 0:
        print("CRITICAL - Updates pending! (" + str(pendingUpdates) + ")")
        sys.exit(CRITICAL)
    else:
        print("UNKNOWN - Unknown error")
        sys.exit(UNKNOWN)


def yumUpdates():
    "Get pending system updates using yum"
    cmdUpdate = '/usr/bin/yum check-update'
    cmdStatus, cmdOutput = runCmd(cmdUpdate)
    if cmdStatus == 0:
        print("OK - No pending updates.")
        sys.exit(OK)
    elif cmdStatus == 100:
        print("CRITICAL - Updates pending!")
        sys.exit(CRITICAL)
    else:
        print("UNKNOWN - Unknown error")
        sys.exit(UNKNOWN)


def main():
    myOs = osData()
    curOs = myOs['system']
    curDist = myOs['dist']
    checkUpdates(curDist)


if __name__ == '__main__':
    main()
