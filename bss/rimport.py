""" This module checks if R_HOME is set and in case R exists as a conda package
"""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson-Lovelace Brain Mapping Center, \
                   University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

from os import path, environ
from sys import stdout, executable
from subprocess import check_output


def check_R_path():
    # Check if R is installed as a conda package in the same environment as bss
    bss_master_path = path.split(path.split(executable)[0])[0]
    r_path = path.join(bss_master_path, 'lib/R')
    if path.exists(r_path):
        # Just set R_HOME to the r path
        environ["R_HOME"] = r_path
        return
    else:
        # R is installed outside the conda installation
        try:
            # Check if R_HOME is set
            R_HOME = environ["R_HOME"]
        except KeyError as keyerr:
            # If R_HOME is not set
            # Check if "R RHOME" returns a valid path
            try:
                Rpath = check_output(["R", "RHOME"])
                # WARNING: ignoring environment value of R_HOME
                environ["R_HOME"] = Rpath
            except OSError as oserr:
                stdout.write('Perhaps R is not installed properly or R_HOME is not set\n')
            except Exception as e:
                stdout.write('\nError: ' + e.message + '\n')
                stdout.write('R_HOME is not set. Please check if R is installed.')
