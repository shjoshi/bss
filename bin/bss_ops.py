#! /usr/local/epd/bin/python
"""
Mathematical operations on BrainSuite data types
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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import argparse
import time
import os
import sys
import traceback
from bss import math_ops


def main():
    parser = argparse.ArgumentParser(description='Perform mathematical/binary operations on Brainsuite data types')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_add = subparsers.add_parser('add', help='add attributes of file 1 and file2 and store in fileout')
    parser_add.add_argument('file1', help='input file 1')
    parser_add.add_argument('file2', help='input file 2')
    parser_add.add_argument('fileout', help='output file')
    parser_add.set_defaults(func=add)

    parser_sub = subparsers.add_parser('sub', help='subtract attributes of file2 from file1 and store in fileout')
    parser_sub.add_argument('file1', help='input file 1')
    parser_sub.add_argument('file2', help='input file 2')
    parser_sub.add_argument('fileout', help='output file')
    parser_sub.set_defaults(func=sub)

    parser_jacdet = subparsers.add_parser('jacdet', help='jacobian determinant of vector fields in an image')
    parser_jacdet.add_argument('filein', help='input image file (nii.gz)')
    parser_jacdet.add_argument('fileout', help='output file with the jacobian determinant (nii.gz)')
    parser_jacdet.add_argument('-sigma', dest='sigma', help='smooth the output first', default=0, type=float)
    parser_jacdet.set_defaults(func=jacdet)

    parser_smooth = subparsers.add_parser('smooth', help='smooth an image')
    parser_smooth.add_argument('filein', help='input image file (nii.gz)')
    parser_smooth.add_argument('fileout', help='output file with the jacobian determinant (nii.gz)')
    parser_smooth.add_argument('-sigma', dest='sigma', help='smooth the output first', default=0, type=float)
    parser_smooth.set_defaults(func=smooth)

    parser_percent_change = subparsers.add_parser('percent_change', help='calculate percent change in attributes')
    parser_percent_change.add_argument('file1', help='input file 1(.dfs)')
    parser_percent_change.add_argument('file2', help='output file 2 (.dfs)')
    parser_percent_change.add_argument('fileout', help='output file')
    parser_percent_change.set_defaults(func=percent_change)

    args = parser.parse_args()
    t = time.time()
    try:
        args.func(args)
    except (ValueError, IOError, NotImplementedError) as err:
        sys.stdout.write('Error: ' + err.message + '\n')

    except Exception as e:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.format_exception_only(type(e), e)
        print traceback.print_exc(file=sys.stdout)

    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.")


def add(args):
    math_ops.add(args.file1, args.file2, args.fileout)


def sub(args):
    math_ops.sub(args.file1, args.file2, args.fileout)


def smooth(args):
    math_ops.smooth_image_file(args.filein, args.fileout, args.sigma)


def jacdet(args):
    math_ops.jacobian_det_image(args.filein, args.fileout, args.sigma)


def percent_change(args):
    math_ops.percent_change(args.file1, args.file2, args.fileout)

if __name__ == '__main__':
    main()
