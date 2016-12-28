#! /usr/local/epd/bin/python

"""
Takes an input attributes file (.mat, .txt) and writes it in the attribute file of the input surface
"""
"""Copyright (C) Shantanu H. Joshi
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"


import argparse
import traceback
import sys
from os.path import splitext
from bss.nimgdata_io import NimgDataio
from bss.excepts import AttributeLengthError


def main():
    parser = argparse.ArgumentParser(description='Write input attribute values to the surface.\n')
    parser.add_argument('input_surface', help='input surface')
    parser.add_argument('attribute_file', help='input attribute file [.mat, .txt]. If a mat file is provided it should only contain a single array variable matching the length of the input surface')
    parser.add_argument('output_surface', help='output surface')

    args = parser.parse_args()

    if splitext(args.attribute_file)[1] != '.mat' and splitext(args.attribute_file)[1] != '.txt':
        raise ValueError('Invalid attribute file' + args.attribute_file +
                         '. Attribute file should have a .mat or a .txt format.\n')

    try:
        NimgDataio.write_attribute_to_surface(args.input_surface, args.attribute_file, args.output_surface)
    except IOError as e:
        sys.stdout.write('Error: Could not read input files.\n')
        print traceback.format_exception_only(type(e), e)
    except AttributeLengthError as e:
        print e.message
    except:
        sys.stdout.write("Something went wrong. Please send this error message to the developers."
                          "\nUnexpected error:" + sys.exc_info()[0])
        sys.stdout.write(traceback.print_exc(file=sys.stdout))


if __name__ == '__main__':
    main()
