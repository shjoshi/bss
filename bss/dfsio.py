""" This module implements file reading and writing functions for the dfs format for BrainSuite
    Also see http://brainsuite.bmap.ucla.edu for the software
"""

"""Copyright (C) Brandon Ayers, Shantanu H. Joshi, David Shattuck,
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

__author__ = "Brandon Ayers"
__copyright__ = "Copyright 2013, Brandon Ayers, Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "ayersb@ucla.edu"

import numpy as np
import struct
import os
import sys

def readdfs(fname):
    class hdr:
        pass

    class NFV:
        pass

    if not os.path.exists(fname):
        raise IOError('\nIOError: File name ' + fname + ' does not exist.')

    fid = open(fname, 'rb')
    hdr.ftype_header = np.fromfile(fid, dtype='S1', count=12)
    if 'DFS' not in ''.join(hdr.ftype_header):
        raise ValueError('Invalid dfs file' + fname)  # TODO: Change this to a custom exception in future
    hdr.hdrsize = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.mdoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.pdoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nTriangles = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nVertices = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nStrips = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.stripSize = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.normals = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.uvStart = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.vcoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.labelOffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.vertexAttributes = np.fromfile(fid, dtype='int32', count=1)[0]
    fid.seek(hdr.hdrsize)
    NFV.faces = np.fromfile(fid, dtype='int32', count=3 * hdr.nTriangles).reshape((hdr.nTriangles, 3))
    NFV.vertices = np.fromfile(fid, dtype='float32', count=3 * hdr.nVertices).reshape((hdr.nVertices, 3))
    if (hdr.normals > 0):
        #print 'reading vertex normals.'
        fid.seek(hdr.normals)
        NFV.normals = np.fromfile(fid, dtype='float32', count=3 * hdr.nVertices).reshape((hdr.nVertices, 3))
    if (hdr.vcoffset > 0):
        #print 'reading vertex colors.'
        fid.seek(hdr.vcoffset)
        NFV.vColor = np.fromfile(fid, dtype='float32', count=3 * hdr.nVertices).reshape((hdr.nVertices, 3))
    if (hdr.uvStart > 0):
        #print 'reading uv coordinates.'
        fid.seek(hdr.uvStart)
        uv = np.fromfile(fid, dtype='float32', count=2 * hdr.nVertices).reshape((hdr.nVertices, 2))
        NFV.u = uv[:, 0]
        NFV.v = uv[:, 1]
    if (hdr.labelOffset > 0):
        #print 'reading vertex labels.'
        fid.seek(hdr.labelOffset)
        #labels are 2 byte unsigned integers, so use unsigned short in python
        NFV.labels = np.fromfile(fid, dtype='uint16', count=hdr.nVertices)
    if (hdr.vertexAttributes > 0):
        #print 'reading vertex attributes.'
        fid.seek(hdr.vertexAttributes)
        NFV.attributes = np.fromfile(fid, dtype='float32', count=hdr.nVertices)
    NFV.name = fname
    fid.close()
    return (NFV)


def readdfsattributes(fname):

    class hdr:
        pass

    class NFV:
        pass

    fid = open(fname, 'rb')
    hdr.ftype_header = np.fromfile(fid, dtype='S1', count=12)
    if 'DFS' not in ''.join(hdr.ftype_header):
        raise ValueError('Invalid dfs file' + fname)  # TODO: Change this to a custom exception in future
    hdr.hdrsize = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.mdoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.pdoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nTriangles = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nVertices = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.nStrips = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.stripSize = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.normals = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.uvStart = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.vcoffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.labelOffset = np.fromfile(fid, dtype='int32', count=1)[0]
    hdr.vertexAttributes = np.fromfile(fid, dtype='int32', count=1)[0]
    attributes = []
    if (hdr.vertexAttributes > 0):
        fid.seek(hdr.vertexAttributes)
        attributes = np.fromfile(fid, dtype='float32', count=hdr.nVertices)
    fid.close()
    return attributes


def writedfs(fname,NFV):
    ftype_header = np.array(['D','F','S','_','L','E',' ','v','2','.','0','\x00']) #DFS_LEv2.0\0
    hdrsize = 184
    mdoffset = 0        # Start of metadata.
    pdoffset = 0       # Start of patient data header.
    nTriangles = len(NFV.faces.flatten()) / 3
    nVertices = len(NFV.vertices.flatten()) / 3
    nStrips = 0
    stripSize = 0
    normals = 0
    uvoffset = 0
    vcoffset = 0
    precision = 0
    labelOffset = 0
    attributes = 0
    orientation = np.matrix(np.identity(4), dtype='int32')
    nextarraypos = hdrsize + 12 * (nTriangles + nVertices)  # Start feilds after the header
    if (hasattr(NFV,'normals')):
        #print 'has normals'
        normals = nextarraypos
        nextarraypos = nextarraypos + nVertices * 12 #12 bytes per normal vector (3 x float32)
    if (hasattr(NFV, 'vColor')):
        #'has vcolor'
        vcoffset = nextarraypos
        nextarraypos = nextarraypos + nVertices * 12 # 12 bytes per color coordinate (3 x float32)
    if (hasattr(NFV, 'u') and hasattr(NFV, 'v')):
        #print 'has uv'
        uvoffset = nextarraypos
        nextarraypos = nextarraypos + nVertices * 8 # 8 bytes per uv coordinate (2 x float32)
    if (hasattr(NFV, 'labels')):
        #print 'has labels'
        labelOffset = nextarraypos
        nextarraypos = nextarraypos + nVertices * 2  # 4 bytes per label (int16)
    if (hasattr(NFV, 'attributes')):
        #print 'has attr'
        attributes = nextarraypos
        nextarraypos = nextarraypos + nVertices * 4  #  4 bytes per attribute (float32)
    fid = open(fname, 'wb')
    fid.write(np.array(ftype_header, 'S1').tostring())
    fid.write(np.array(hdrsize, 'int32').tostring())
    fid.write(np.array(mdoffset, 'int32').tostring())
    fid.write(np.array(pdoffset, 'int32').tostring())
    fid.write(np.array(nTriangles, 'int32').tostring())
    fid.write(np.array(nVertices, 'int32').tostring())
    fid.write(np.array(nStrips, 'int32').tostring())
    fid.write(np.array(stripSize, 'int32').tostring())
    fid.write(np.array(normals, 'int32').tostring())
    fid.write(np.array(uvoffset, 'int32').tostring())
    fid.write(np.array(vcoffset, 'int32').tostring())
    fid.write(np.array(labelOffset, 'int32').tostring())
    fid.write(np.array(attributes, 'int32').tostring())
    fid.write(np.zeros([1, 4 + 15 * 8], 'uint8').tostring())
    fid.write(np.array((NFV.faces), 'int32').tostring())
    fid.write(np.array(NFV.vertices, 'float32').tostring())
    if (normals > 0):
        #print 'writing normals' 
        fid.write(np.array(NFV.normals, 'float32').tostring())
    if vcoffset > 0:
        #print 'writing color'
        fid.write(np.array(NFV.vColor, 'float32').tostring())
    if uvoffset > 0:
        #print 'writing uv'
        fid.write(np.array([NFV.u.flatten(), NFV.v.flatten()], 'float32').tostring())
    if (labelOffset > 0):
        #print 'writing labels' 
        fid.write(np.array(NFV.labels, 'int16').tostring())
    if (attributes > 0):
        #print 'writing attributes' 
        fid.write(np.array(NFV.attributes, 'float32').tostring())
    fid.close()
