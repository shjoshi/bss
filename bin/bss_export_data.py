#! /usr/local/epd/bin/python

"""
Save roi stats from a list of subjects to a single csv for group analysis
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
import traceback
import sys
from os.path import splitext
from bss.nimgdata_io import NimgDataio


def main():
    parser = argparse.ArgumentParser(description='Export cortical attributes from a list of subjects to a single mat file for group analysis.\n')
    parser.add_argument('filelist', help='list of file path names for all subjects')
    parser.add_argument('outputfile', help='output mat file containing pointwise attribute values for all subjects')

    args = parser.parse_args()
    bss_export_data(args.filelist, args.outputfile)


def bss_export_data(filelist, outputfile):

    if splitext(outputfile)[1] != '.mat':
        sys.stdout.write('Output file should have a .mat format.\n')
        return

    try:
        NimgDataio.export_data_to_mat(filelist, outputfile)
    except IOError as e:
        sys.stdout.write('Error: Could not read file' + filelist + '\n')
        print traceback.format_exception_only(type(e), e)
    except:
        sys.stdout.write("Something went wrong. Please send this error message to the developers."
                          "\nUnexpected error:" + sys.exc_info()[0])
        sys.stdout.write(traceback.print_exc(file=sys.stdout))


if __name__ == '__main__':
    main()
