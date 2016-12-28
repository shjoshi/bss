""" This module sets the matplotlib backend and imports required matplotlib modules
"""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson-Lovelace Brain Mapping Center, \
                   University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"


def init():
    import matplotlib as mpl
    mpl.use('pdf')  # Set backend to pdf
