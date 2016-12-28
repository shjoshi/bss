"""
Convert a ROI sphere (xml) to mask image
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import argparse
import traceback
import sys
from bss.math_ops import roi_sphere_to_mask
import os
import time


def main():
    parser = argparse.ArgumentParser(description='Convert a sphere ROI drawn in BrainSuite to a mask image\n')
    parser.add_argument('roixml', help='input ROI xml file')
    parser.add_argument('template', help='input template image (.nii.gz). This is only used to set the dimensions of the output image')
    parser.add_argument('mask', help='output mask volume (.nii.gz). The output will be the same dimensions as the template')
    parser.add_argument('-roi', dest='roi', help='index of the roi in the xml file, 1, 2, etc.', type=int, required=True)

    args = parser.parse_args()

    t = time.time()
    bss_sphere_to_mask(args.roixml, args.template, args.mask, args.roi)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_sphere_to_mask(roixml, template, mask, roi):

    try:
        roi_sphere_to_mask(roixml, template, mask, roi)
    except (IOError, TypeError, IndexError) as e:
        sys.stdout.write(e.args[0] + '\n')
    except:
        sys.stdout.write("Something went wrong. Please send this error message to the developers.")
        sys.stdout.write(traceback.print_exc(file=sys.stdout))

if __name__ == '__main__':
    main()

