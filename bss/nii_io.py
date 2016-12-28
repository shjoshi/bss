""" This module implements file reading and writing functions for the dfs format for BrainSuite
    Also see http://brainsuite.bmap.ucla.edu for the software
"""

"""Copyright (C) Shantanu H. Joshi, David Shattuck,
Brain Mapping Center, University of California Los Angeles

Bss is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

Bss is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2015, Shantanu H. Joshi, Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import numpy as np
import struct
import os
import sys
import nibabel as nib


def readnii(fname):

    if not os.path.exists(fname):
        raise IOError('\nIOError: File name ' + fname + ' does not exist.')

    try:
        nii = nib.load(fname)
        return nii
    except Exception as e:
        sys.stdout.write(str(e) + '\n')


def writenii(fname, nii):

    if not os.path.exists(os.path.dirname(fname)) and os.path.dirname(fname):
        raise IOError('\nIOError: File path ' + fname + ' does not exist.')

    try:
        nib.save(nii, fname)
        return
    except Exception as e:
        sys.stdout.write(str(e) + '\n')


