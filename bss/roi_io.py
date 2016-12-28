#! /usr/local/epd/bin/python
"""
I/O for roiwise.stats.txt file
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


import numpy as np
import struct
import os
import sys
import pandas

measure_dict = {'gmthickness': 'Mean_Thickness(mm)',
                'gmvolume': 'GM_Volume(mm^3)',
                'area': 'Cortical_Area_pial(mm^2)',
                'swmFA': 'swmFA',
                'swmMD': 'swmMD',
                'swmRD': 'swmRD',
                'swmAD': 'swmAD',
                }


def read_roistats_txt(fname, roiid='', roimeasure='gmthickness'):

    # TODO: Currently this is hardcoded. Could be moved to a config file in the future
    # TODO: This dict is getting repeated in multiple files. Find a way to have a single definition
    if not os.path.exists(fname):
        raise IOError('File name ' + fname + ' does not exist.')

    # Check if file is a roiwise.stats.txt file.
    fid = open(fname, 'rt')
    first_line = fid.readline()
    fid.close()
    # Check if first 6 characters are ROI_ID
    if first_line[:6] == 'ROI_ID':
        roiwise_stats = pandas.read_table(fname, na_values='NaN', keep_default_na=False, index_col=0)
        if not roiid:  # Read all ROIs
            return np.array(roiwise_stats[measure_dict[roimeasure]])
        else:
            if not np.isnan(roiwise_stats.loc[roiid, measure_dict[roimeasure]].values).any():
                return roiwise_stats.loc[roiid, measure_dict[roimeasure]].values
            else:
                raise ValueError('One or more ROIs ' + ', '.join([str(i) for i in roiid]) + ' in ' + fname + ' may be missing or contain Nans.\n')
    else:
        raise IOError('The file ' + fname + ' is not a valid roiwise.stats.txt file.\n')
