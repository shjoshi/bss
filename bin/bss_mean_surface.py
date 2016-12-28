#! /usr/local/epd/bin/python

"""
Create an average dfs surface for a set of registered dfs surfaces. Attributes are averaged if present
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
import os
import pandas
from bss import dfsio
import sys
import traceback
import numpy as np
from bss import rimport

rimport.check_R_path()


def main():
    parser = argparse.ArgumentParser(description='Creates a Euclidean average dfs surface from a set of registered dfs surfaces. '
                                                 'Attributes if present are also averaged. Input is a text file OR a csv file with the \n')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--txt', metavar='TXT_FILE', help='Text file containing a list of dfs surfaces')
    group.add_argument('--csv', nargs=2, metavar=('CSV_FILE', 'FILE_COLUMN_NAME'),
                       help='Demographics csv file containing a column for file names followed by the column name')
    parser.add_argument('dfsfilename', help='output dfs file name for the mean surface')
    args = parser.parse_args()
    bss_mean_surface(args)


def bss_mean_surface(args):
    try:
        # Parse the arguments
        if args.txt:    # If txt file present
            fid = open(args.txt, 'rt')
            filelist = [filename.rstrip('\n') for filename in fid.readlines()]
        elif args.csv:  # If csv file present
            demographic_data = pandas.read_csv(args.csv[0])
            # Iterate over all columns, and check if any of the values
            # are NaN for missing data
            # TODO: This code is repeated.
            for columns in demographic_data.columns.values:
                if len(np.where(demographic_data[columns].isnull())[0]) > 0:
                    sys.stdout.write('Error: Some data may be missing from the demographics file: ' + args.csv[0] + '. ' +
                                     '\nIf nothing seems wrong at the first glance and if its a csv file, please open it in a '
                                     '\nplain text editor and check if there are missing values, rows, or columns.' +
                                     '. Will quit now.\n')
                    return

            filelist = demographic_data[args.csv[1]]

        # Read the file list and compute the average of the coordinates and attributes
        surf_array = []
        for fname in filelist:
            surf_array.append(dfsio.readdfs(fname))

        # Check if all surfaces have same number of vertices
        nVertices = len(surf_array[0].vertices)
        s1_average = surf_array[0]

        for i in range(1, len(surf_array)):
            if len(surf_array[i].vertices) == nVertices:
                s1_average.vertices += surf_array[i].vertices
                if surf_array[i].attributes.any():
                    s1_average.attributes += surf_array[i].attributes
            else:
                sys.stdout.write('Not all surfaces have the same number of vertices. Exiting...\n')
                return
        s1_average.vertices /= len(surf_array)
        s1_average.attributes /= len(surf_array)
        dfsio.writedfs(args.dfsfilename, s1_average)

    except:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    main()
