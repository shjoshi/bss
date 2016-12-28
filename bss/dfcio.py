""" This module implements file reading and writing functions for the dfc format for BrainSuite
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

__author__ = "Shantanu H . Joshi"
__copyright__ = "Copyright 2013, Brandon Ayers, Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"

import numpy as np
import struct
import os
import sys


def readdfc(filename):
    class hdr:
        pass

    class NFV:
        pass

    Curves = []

    fid = open(filename, 'rb')

    hdr.magic = np.fromfile(fid, dtype='S1', count=8)
    hdr.version = np.fromfile(fid, dtype='S1', count=4)
    hdr.hdrsize = np.fromfile(fid, dtype='int32', count=1)
    hdr.dataStart = np.fromfile(fid, dtype='int32', count=1)
    hdr.mdoffset = np.fromfile(fid, dtype='int32', count=1)
    hdr.pdoffset = np.fromfile(fid, dtype='int32', count=1)
    hdr.nContours = np.fromfile(fid, dtype='int32', count=1)

    fid.seek(hdr.mdoffset, os.SEEK_SET)
    Mdata = np.fromfile(fid, dtype='S1', count=hdr.dataStart - hdr.mdoffset)
    hdr.xmlstr = "".join(Mdata)

    fid.seek(hdr.dataStart, os.SEEK_SET)
    for ctno in np.arange(0, hdr.nContours):
        nopts = np.fromfile(fid, dtype='int32', count=1)

        XYZ = np.fromfile(fid, dtype='float', count=3 * nopts)
        XYZ = np.transpose(np.reshape(XYZ, (3, nopts), order='F'))
        Curves.append(XYZ)

    fid.close()
    if len(Curves) == 28:
        sys.stdout.write('This file ' + filename + ' is traced using a 28 curve protocol\n')
    elif len(Curves) == 26:
        sys.stdout.write('This file ' + filename + ' is traced using a 26 curve protocol\n')
    else:
        sys.stdout.write('This file ' + filename + ' is traced using an unknown protocol with ' +
                         len(Curves) + ' number of curves. Now Exiting...\n')
        return

    return Curves, hdr
