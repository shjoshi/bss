#! /usr/local/epd/bin/python
"""
This program resamples a given dfs surface to a target dfs surface.
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
__copyright__ = "Copyright 2014, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "sjoshi@bmap.ucla.edu"


import sys
import numpy as np
from scipy.interpolate import griddata
import argparse
from bss import dfsio


def main():
    parser = argparse.ArgumentParser(description='This program resamples a surface to a target')
    parser.add_argument('src', help='source dfs surface')
    parser.add_argument('src_target', help='source dfs surface registered to atlas')
    parser.add_argument('src_resamp_to_tgt', help='output resampled surface')

    args = parser.parse_args()
    bss_resample_surface_to_target(args.src, args.src_target, args.src_resamp_to_tgt)


def bss_resample_surface_to_target(srcfile, src_regfile, resampfile):

    surf_src = dfsio.readdfs(srcfile)
    surf_src_reg = dfsio.readdfs(src_regfile)

    surf_src.uv = np.c_[surf_src.u, surf_src.v]
    surf_src_reg.uv = np.c_[surf_src_reg.u, surf_src_reg.v]

    sys.stdout.write("Resampling source to target...")
    sys.stdout.write("x ")
    res_x = griddata(surf_src.uv, surf_src.vertices[:, 0], surf_src_reg.uv, method='nearest')
    sys.stdout.write("y ")
    res_y = griddata(surf_src.uv, surf_src.vertices[:, 1], surf_src_reg.uv, method='nearest')
    sys.stdout.write("z ")
    res_z = griddata(surf_src.uv, surf_src.vertices[:, 2], surf_src_reg.uv, method='nearest')
    sys.stdout.write("Done.\n")

    res_vertices = np.zeros((surf_src_reg.vertices.shape[0], 3))
    res_vertices[:, 0] = res_x
    res_vertices[:, 1] = res_y
    res_vertices[:, 2] = res_z

    if len(surf_src.attributes) > 0:
        sys.stdout.write("Resampling attributes to target ...")
        res_attributes = griddata(surf_src.vertices, surf_src.attributes, res_vertices, method='nearest')
        sys.stdout.write("Done.\n")
    else:
        res_attributes = []

    if len(surf_src.labels) > 0:
        sys.stdout.write("Resampling labels to target ...")
        res_labels = griddata(surf_src.vertices, surf_src.labels, res_vertices, method='nearest')
        sys.stdout.write("Done.\n")
    else:
        res_labels = []

    class surf_resamp:
        pass

    surf_resamp.vertices = res_vertices
    surf_resamp.faces = surf_src_reg.faces
    surf_resamp.attributes = res_attributes
    surf_resamp.labels = res_labels
    dfsio.writedfs(resampfile, surf_resamp)

    return None

if __name__ == '__main__':
    main()
