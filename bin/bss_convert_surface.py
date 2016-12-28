#! /usr/local/epd/bin/python

"""
Convert surface formats
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"


import argparse
import os
import sys
from bss import surfio



def bss_convert_surface(surfin, surfout, surf_conn=None):
    sin_name, sin_ext = os.path.splitext(surfin)

    if surfin == surfout:
        sys.stdout.write("Error: Same input and output formats " + sin_ext + ". Exiting without saving anything...")
        return None

    in_faces = []
    if sin_ext == ".ucf":
        if surf_conn is None:
            sys.stdout.write('Attempting to convert ucf (point set) to vtp (triangular mesh). '
                             'A template connectivity surface is required. Exiting without saving...')
            return None
        else:
            conn_coords, conn_faces, conn_attributes, isMultilevelUCF = surfio.readsurface_new(surf_conn)
            in_faces = conn_faces

    in_coords, temp_faces, in_attributes, isMultilevelUCF = surfio.readsurface_new(surfin)
    if not len(in_faces):
        in_faces = temp_faces

    surfio.writesurface_new(surfout, in_coords, in_faces, in_attributes)

    return None


def main():
    parser = argparse.ArgumentParser(description='Convert Surface formats.')
    parser.add_argument('-surfin', dest='surfin', help='input surface [ucf,vtp]', required=True)
    parser.add_argument('-surfout', dest='surfout', help='output surface [ucf,vtp]', required=True)
    parser.add_argument('-conn', dest='surfconn', default="", help='template surf with connectivity [vtp,pial]',
                        required=False)
    args = parser.parse_args()
    bss_convert_surface(args.surfin, args.surfout, args.surfconn)
    return None

if __name__ == '__main__':
    main()

