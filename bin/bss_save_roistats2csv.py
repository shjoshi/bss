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
import pandas
import numpy as np
from collections import OrderedDict


def main():
    parser = argparse.ArgumentParser(description='Save roi stats from a list of subjects to a single csv for group analysis.\n')
    parser.add_argument('filelist', help='list of path name to roiwise.stats.txt for all subjects')
    parser.add_argument('outcsv', help='output csv file containing stats for all subjects')
    parser.add_argument('-meas', help='measure to extract', choices=['gmthickness', 'gmvolume', 'area', 'swmFA', 'swmMD',
                                                                     'swmRD', 'swmAD'], default='gmthickness')

    args = parser.parse_args()
    bss_save_roistats2csv(args.filelist, args.meas, args.outcsv)


def bss_save_roistats2csv(filelist, measure, outcsv):

    # TODO: Currently this is hardcoded. Could be moved to a config file in the future
    # TODO: Currently only the pial area is returned. Could return different inner and mid areas in the future
    measure_dict = {'gmthickness': 'Mean_Thickness(mm)',
                    'gmvolume': 'GM_Volume(mm^3)',
                    'area': 'Cortical_Area_pial(mm^2)',
                    'swmFA': 'swmFA',
                    'swmMD': 'swmMD',
                    'swmRD': 'swmRD',
                    'swmAD': 'swmAD',
                    }
    try:
        fid = open(filelist, 'rt')
        filenames = [filename.rstrip('\n') for filename in fid.readlines()]

        subject_dict = OrderedDict()

        # Read the first file to get the ROI_IDs
        roiwise_stats = pandas.read_table(filenames[0], na_values='NaN', keep_default_na=False)
        subject_dict['subjID'] = np.array(roiwise_stats['ROI_ID'], dtype=np.uint32)
        subject_dict[filenames[0]] = np.array(roiwise_stats[measure_dict[measure]])
        print filenames[0]
        filenames.pop(0)

        for fname in filenames:
            roiwise_stats = pandas.read_table(fname)
            subject_dict[fname] = np.array(roiwise_stats[measure_dict[measure]])
            print fname

        subject_dataframe = pandas.DataFrame.from_dict(subject_dict, orient='index')
        subject_dataframe = subject_dataframe.convert_objects(convert_numeric=True)
        sys.stdout.write('Saving csv file ' + outcsv + '...')
        subject_dataframe.to_csv(outcsv, header=False)
        sys.stdout.write('Done.\n')
    except IOError as e:
        sys.stdout.write('Error: Perhaps a roiwise txt file is missing\n')
        # print traceback.format_exception_only(type(e), e)
    except KeyError as e:
        sys.stdout.write('KeyError: ' + e.message)
        sys.stdout.write('\nError: Missing column name {0:s} in {1:s}'.format(measure, fname) + '\n')
    except:
         print "Something went wrong. Please send this error message to the developers." \
               "\nUnexpected error:", sys.exc_info()[0]
         print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()
