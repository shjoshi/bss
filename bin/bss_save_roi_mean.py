#! /usr/local/epd/bin/python

"""
Save mean values of attributes for ROI labels
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
__email__ = "s.joshi@ucla.edu"


import argparse
from bss import dfsio
import sys
import csv
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Convert p-values to rgb color. Assumes p-values already exist as attributes in the dfs file.\n')
    parser.add_argument('dfs_surface_in', help='input dfs surface')
    parser.add_argument('label_ids', help='comma separated list of label identifiers')
    parser.add_argument('roi_mean_csv', help='csv file of label numbers')
    parser.add_argument('-atlas', dest='atlas', help='atlas file containing label information', required=False)
    parser.add_argument('-merge', dest='merge', help='if true, then merge labels for all comma separated label identifiers',
                        required=False, default=False, action='store_true')

    args = parser.parse_args()
    bss_save_roi_mean(args.dfs_surface_in, args.atlas, args.label_ids, args.roi_mean_csv, args.merge)


def bss_save_roi_mean(surfin, atlas, orig_label_ids, roi_mean_csv, merge_labels):
    s1 = dfsio.readdfs(surfin)
    if not atlas:  # If atlas is not provided then surfin should contain labels
        if not hasattr(s1, 'labels'):
            sys.stdout.write('Error: The surface ' + surfin + ' is missing label values. Try providing an atlas file.\n')
            return

    if not hasattr(s1, 'attributes'):
        sys.stdout.write('Error: The surface ' + surfin + ' is missing attribute values.\n')
        return
    s1_atlas = dfsio.readdfs(atlas)

    roi_mean = []
    label_ids = orig_label_ids.split(',')
    labels_to_save = []

    for label in label_ids:
        idx = np.where(s1_atlas.labels == int(label))
        if idx[0].any():
            labels_to_save.append(label)
            roi_mean.append(np.mean(s1.attributes[idx[0]]))
        else:
            sys.stdout.write('Could not find label identifier in atlas. Skipping label ' + label + '.\n')

    if merge_labels:
        roi_mean = [np.mean(roi_mean)]
        labels_to_save = [orig_label_ids]

    dataout = [labels_to_save, roi_mean]
    dataout = zip(*dataout)
    sys.stdout.write('Saving the indices and means of roi attributes...')
    sys.stdout.flush()
    f = open(roi_mean_csv, 'wt')
    w = csv.writer(f)
    w.writerows(dataout)
    f.close()
    sys.stdout.write('Done.\n')

if __name__ == '__main__':
    main()
